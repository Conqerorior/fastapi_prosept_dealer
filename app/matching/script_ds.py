"""Функция от DS."""

import re

import lightgbm as lgb
import nltk
import numpy as np
import pandas as pd
import torch
import transformers
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from scipy.spatial.distance import cdist
from sklearn.model_selection import train_test_split
from tqdm import tqdm

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
pd.options.mode.chained_assignment = None  # default='warn'


def matching_training(lst_dict_pr, lst_dict_dr, lst_dict_k, nm: str = 'name'):
    """Функция для обучения модели.

    Args:
        - lst_dict_pr (List[Dict]): Список словарей карточек Просепт.
        - lst_dict_dr (List[Dict]): Список словарей карточек дилеров для обучения.
        - lst_dict_k (List[Dict]): Список словарей внешних ключей.
        - nm (str): Столбец, по которому происходит сравнение.

    Returns:
        - Возвращает обученную модель, которую надо подставить на вход в функцию предсказаний.
    """
    data_mdp = pd.DataFrame(lst_dict_dr)
    data_mp = pd.DataFrame(lst_dict_pr)
    data_mpdk = pd.DataFrame(lst_dict_k)

    def remove_row_dealer(data_mp, data_mdp, data_mpdk):
        """Функция для удаления строк из данных от дилеров.

        Удаляются строки, для которых нет значений id продуктов
        из данных производителя и строки, id из данных производителя
        которых совпадают с id удаляемых строк из данных производителя
        с отсутствующими описаниями.
        """
        test_null = data_mdp.merge(data_mpdk,
                                   how='left',
                                   left_on='product_key',
                                   right_on='key').loc[:, ['product_key',
                                                           'key',
                                                           'product_id']]
        ind_drop = test_null.loc[test_null['product_id'].isnull()].index.values
        data_mdp.drop(ind_drop, axis=0, inplace=True)

        id_drop = data_mp.loc[data_mp[nm].isnull()]['id']
        drop = data_mpdk.loc[data_mpdk['product_id'].isin(id_drop), ['key',
                                                                     'dealer_id']]
        ind_drop_mdp = []
        for k, v in zip(drop['key'], drop['dealer_id']):
            ind_drop_mdp.extend(list(data_mdp.loc[(data_mdp['product_key'] == k)
                                                  & (data_mdp[
                                                         'dealer_id'] == v)].index.values))
        data_mdp.drop(ind_drop_mdp, axis=0, inplace=True)

        data_mdp.reset_index(drop=True, inplace=True)

        return

    remove_row_dealer(data_mp, data_mdp, data_mpdk)

    # удаляем пропуски в столбце name
    data_mp.dropna(subset=[nm], inplace=True)
    data_mp.reset_index(drop=True, inplace=True)

    data_mp_name = data_mp[['id', nm]]

    def separation(s):
        """
        Функция для удаления знаков препинания,
        а также для расклеивания склеенных слов,
        то есть разделения пробелами латиницы от кириллицы,
        чисел от букв и слов в верхнем регистре от слов
        в нижнем регистре в склеенных словах.
        """

        s = re.sub(r'[^\w\s]', ' ', s)
        lat = re.findall(r"[a-zA-Z]+", s)
        num = re.findall(r"\d+", s)
        up = re.findall(r"[А-Я]+", s)
        for i in lat:
            s = s.replace(i, ' ' + i + ' ')
        for i in num:
            s = s.replace(i, ' ' + i + ' ')
        for i in up:
            if len(i) > 1:
                s = s.replace(i, ' ' + i + ' ')
        s = ' '.join([i.lower() for i in s.split()])
        return s

    def tokenize(df, name):
        """
        Функция для подготовки к векторизации: разделение склеенных слов,
        токенизация, лемматизация, стем, избавление от стоп-слов,
        приведение к нижнему регистру.
        """

        stopword_en = stopwords.words('english')
        stopword_ru = stopwords.words('russian')
        porter = PorterStemmer()
        lemmatizer = WordNetLemmatizer()
        tokenized = []
        for q in df[name]:
            q = separation(q)
            q = word_tokenize(q)
            q = [lemmatizer.lemmatize(i) for i in q if
                 (i not in stopword_en) and
                 (i not in stopword_ru)]
            q = [porter.stem(i) for i in q]
            tokenized.append(q)
        name_tok = []
        for i in tokenized:
            name_tok.append(' '.join(i))
        df[name + '_tok'] = name_tok
        return df

    # функция tokenize для данных от производителя
    # и для данных от диллеров
    tokenize(data_mp_name, nm)
    tokenize(data_mdp, 'product_name')

    data_mp_id = data_mp_name.loc[:, ['id', nm + '_tok']]
    data_mp_name.drop([nm, 'id'], axis=1, inplace=True)

    # трансформер LaBSE
    bert_name = 'sentence-transformers/LaBSE'
    enc_tokenizer = transformers.AutoTokenizer.from_pretrained(bert_name)
    encoder = transformers.AutoModel.from_pretrained(bert_name)

    data_train = pd.concat([data_mp_name[nm + '_tok'],
                            data_mdp['product_name_tok']], axis=0)

    def embeddings(data):
        """
        Функция для получения эмбеддингов
        """
        tokenized = data.apply(lambda x: enc_tokenizer.encode(x,
                                                              max_length=512,
                                                              truncation=True,
                                                              add_special_tokens=True))
        max_len = 0
        for i in tokenized.values:
            if len(i) > max_len:
                max_len = len(i)

        padded = np.array(
            [i + [0] * (max_len - len(i)) for i in tokenized.values])
        attention_mask = np.where(padded != 0, 1, 0)

        batch_size = 32
        embeddings = []
        for i in tqdm(range(padded.shape[0] // batch_size)):
            batch = torch.LongTensor(
                padded[batch_size * i:batch_size * (i + 1)])
            attention_mask_batch = torch.LongTensor(
                attention_mask[batch_size * i:batch_size * (i + 1)])
            with torch.no_grad():
                batch_embeddings = encoder(batch,
                                           attention_mask=attention_mask_batch)
            embeddings.append(batch_embeddings[0][:, 0, :].numpy())

        features = np.concatenate(embeddings)
        features = pd.DataFrame(features)

        batch = torch.LongTensor(padded[features.shape[0]:])
        attention_mask_batch = torch.LongTensor(
            attention_mask[features.shape[0]:])
        with torch.no_grad():
            batch_embeddings = encoder(batch,
                                       attention_mask=attention_mask_batch)
        embeddings.append(batch_embeddings[0][:, 0, :].numpy())

        features = np.concatenate(embeddings)
        features = pd.DataFrame(features)

        return features

    features = embeddings(data_train)

    features_mp = features[:data_mp.shape[0]]
    features_mdp = features[data_mp.shape[0]:]

    # рассчёт расстояний
    res = cdist(features_mdp.values, features_mp.values, metric='euclidean')

    # сортировка расстояний
    res = pd.DataFrame(res)
    res_sort = pd.DataFrame([np.sort(res.iloc[i, :]) for i in
                             range(res.shape[0])])

    # фрэйм отсортированных расстояний в значениях id
    res_lm = pd.DataFrame(
        [np.argsort(res.iloc[i, :]) for i in range(res.shape[0])])

    df_res_lm = pd.DataFrame(
        [[data_mp_id.loc[i, 'id'] for i in res_lm.loc[j, :]] for j in
         range(res_lm.shape[0])])

    testlm = data_mdp.merge(data_mpdk,
                            how='left',
                            left_on='product_key',
                            right_on='key').loc[:, ['product_key',
                                                    'key',
                                                    'product_id']]

    testlm = pd.concat([testlm, df_res_lm], axis=1)

    # заполнение 0 и 1 фрэйма с id, где 1 означает верный id
    for j in range(testlm.shape[0]):
        df_res_lm.loc[j, :] = np.where(
            df_res_lm.loc[j, :].values == testlm.loc[
                j, 'product_id'], 1, 0)

    # целевая переменная - номер столбца, в котором стоит 1,
    # то есть верного id в отсортированном фрэйме
    for j in range(df_res_lm.shape[0]):
        df_res_lm.loc[j, 'target'] = (df_res_lm.loc[j, :].
                                      values.
                                      tolist().
                                      index(1))

    # разделение данных с отсортированными
    # значениями расстояний на выборки для обучения модели
    X_train, X_test, Y_train, Y_test = train_test_split(res_sort,
                                                        df_res_lm.target)

    params = {
        'objective': 'multiclass',
        'num_class': X_train.shape[1],
        'metric': 'multi_logloss',
        'verbose': -1,
        'learning_rate': 0.01,
        'max_depth': 15,
        'num_leaves': 17,
        'feature_fraction': 0.4,
        'bagging_fraction': 0.6,
        'bagging_freq': 17
    }

    train_data = lgb.Dataset(X_train, label=Y_train)
    valid_data = lgb.Dataset(X_test, label=Y_test, reference=train_data)

    # обучение модели LGBM для мультиклассовой классификации
    num_round = 100
    model = lgb.train(params,
                      train_data,
                      num_round,
                      valid_sets=[valid_data])

    return model, features_mp


def matching_predict(lst_dict_pr, lst_dict_tst, model_embeddings_pr, k=5, nm='name'):
    """Функция для предсказания.

    Args:
        - lst_dict_pr (List[Dict]): Список словарей карточек Просепт.
        - lst_dict_dr (List[Dict]): Список словарей карточек дилеров для обучения.
        - model_embeddings: Обученная модель и эмбеддинги (два объекта из
          возвращения функции для обучения).
        - k (int): колличество выводимых id товаров производителя
          для каждой карточки диллера (по умолчанию равно 5).
        - nm (str): Столбец, по которому происходит сравнение.
    """

    data_mdp_test = pd.DataFrame(lst_dict_tst)
    data_mp = pd.DataFrame(lst_dict_pr)

    # удаляем пропуски в столбце name
    data_mp.dropna(subset=[nm], inplace=True)
    data_mp.reset_index(drop=True, inplace=True)

    def separation(s):
        """
        Функция для удаления знаков препинания,
        а также для расклеивания склеенных слов,
        то есть разделения пробелами латиницы от кириллицы,
        чисел от букв и слов в верхнем регистре от слов
        в нижнем регистре в склеенных словах.
        """

        s = re.sub(r'[^\w\s]', ' ', s)
        lat = re.findall(r"[a-zA-Z]+", s)
        num = re.findall(r"\d+", s)
        up = re.findall(r"[А-Я]+", s)
        for i in lat:
            s = s.replace(i, ' ' + i + ' ')
        for i in num:
            s = s.replace(i, ' ' + i + ' ')
        for i in up:
            if len(i) > 1:
                s = s.replace(i, ' ' + i + ' ')
        s = ' '.join([i.lower() for i in s.split()])
        return s

    def tokenize(df, name):
        """
        Функция для подготовки к векторизации: разделение склеенных слов,
        токенизация, лемматизация, стем, избавление от стоп-слов,
        приведение к нижнему регистру.
        """

        stopword_en = stopwords.words('english')
        stopword_ru = stopwords.words('russian')
        porter = PorterStemmer()
        lemmatizer = WordNetLemmatizer()
        tokenized = []
        for q in df[name]:
            q = separation(q)
            q = word_tokenize(q)
            q = [lemmatizer.lemmatize(i) for i in q if
                 (i not in stopword_en) and
                 (i not in stopword_ru)]
            q = [porter.stem(i) for i in q]
            tokenized.append(q)
        name_tok = []
        for i in tokenized:
            name_tok.append(' '.join(i))
        df[name + '_tok'] = name_tok
        return df

    # функция tokenize для данных от диллера
    tokenize(data_mdp_test, 'product_name')

    data_mp_id = pd.DataFrame(data_mp.loc[:, 'id'])

    # трансформер LaBSE
    bert_name = 'sentence-transformers/LaBSE'
    enc_tokenizer = transformers.AutoTokenizer.from_pretrained(bert_name)
    encoder = transformers.AutoModel.from_pretrained(bert_name)

    data_test = data_mdp_test['product_name_tok']

    def embeddings(data):
        """
        Функция для получения эмбеддингов
        """
        tokenized = data.apply(lambda x: enc_tokenizer.encode(x,
                                                              max_length=512,
                                                              truncation=True,
                                                              add_special_tokens=True))
        max_len = 0
        for i in tokenized.values:
            if len(i) > max_len:
                max_len = len(i)

        padded = np.array(
            [i + [0] * (max_len - len(i)) for i in tokenized.values])
        attention_mask = np.where(padded != 0, 1, 0)

        batch_size = 32
        embeddings = []
        for i in tqdm(range(padded.shape[0] // batch_size)):
            batch = torch.LongTensor(
                padded[batch_size * i:batch_size * (i + 1)])
            attention_mask_batch = torch.LongTensor(
                attention_mask[batch_size * i:batch_size * (i + 1)])
            with torch.no_grad():
                batch_embeddings = encoder(batch,
                                           attention_mask=attention_mask_batch)
            embeddings.append(batch_embeddings[0][:, 0, :].numpy())

        if embeddings:
            features = np.concatenate(embeddings)
            features = pd.DataFrame(features)
        else:
            features = pd.DataFrame([])

        batch = torch.LongTensor(padded[features.shape[0]:])
        attention_mask_batch = torch.LongTensor(
            attention_mask[features.shape[0]:])
        with torch.no_grad():
            batch_embeddings = encoder(batch,
                                       attention_mask=attention_mask_batch)
        embeddings.append(batch_embeddings[0][:, 0, :].numpy())

        features = np.concatenate(embeddings)
        features = pd.DataFrame(features)

        return features

    features = embeddings(data_test)

    features_mp = model_embeddings_pr[1]
    features_mdp = features

    # расчёт расстояний
    res_t = cdist(features_mdp.values,
                  features_mp.values,
                  metric='euclidean')

    res_t = pd.DataFrame(res_t)

    # фрэйм отсортированных расстояний
    res_sort_t = pd.DataFrame(
        [np.sort(res_t.iloc[i, :]) for i in range(res_t.shape[0])])
    res_lm_t = pd.DataFrame(
        [np.argsort(res_t.iloc[i, :]) for i in range(res_t.shape[0])])
    df_res_lm_t = pd.DataFrame(
        [[data_mp_id.loc[i, 'id'] for i in res_lm_t.loc[j, :]] for j in
         range(res_lm_t.shape[0])])

    model = model_embeddings_pr[0]
    # предсказание для теста (данных от дилеров)
    y_pred_all = model.predict(res_sort_t,
                               num_iteration=model.best_iteration)

    # выделение k самых вероятных объектов из
    # данных производителя для каждой строки дилера
    df_ind_all = pd.DataFrame(
        [np.argsort(y_pred_all[i])[-1: -(k + 1): -1] for i in
         range(y_pred_all.shape[0])])

    # итоговый фрэйм с k самых вероятных id
    result = pd.DataFrame(
        [[df_res_lm_t.loc[i, df_ind_all.loc[i, :][j]] for j in range(k)]
         for i in range(df_ind_all.shape[0])])
    result.columns = [str(i) for i in range(1, k + 1)]

    res_k = result.to_dict('records')

    return res_k
