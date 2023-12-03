import re

import lightgbm as lgb
import nltk
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from scipy.spatial.distance import cdist
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
pd.options.mode.chained_assignment = None  # default='warn'


def matching_training(lst_dict_pr, lst_dict_dr, lst_dict_k):
    """
    ФУНКЦИЯ ДЛЯ ОБУЧЕНИЯ
    Возвращает обученную модель,
    которую надо подставить на вход в функцию предсказаний:

      -lst_dict_pr список словарей карточек производителя
      -lst_dict_dr список словарей карточек диллеров для обучения
      -lst_dict_k список словарей внешних ключей.
    """
    data_mdp = pd.DataFrame(lst_dict_dr)
    data_mp = pd.DataFrame(lst_dict_pr)
    data_mpdk = pd.DataFrame(lst_dict_k)

    # удаление строк из данных от дилеров,
    # для которых нет значений id продуктов
    # из данных производителя (для обучения модели)
    test_null = data_mdp.merge(
        data_mpdk,
        how='left',
        left_on='product_key',
        right_on='key').loc[:, ['product_key',
                                'key',
                                'product_id']]
    ind_drop = test_null.loc[test_null['product_id'].isnull()].index.values
    data_mdp.drop(ind_drop, axis=0, inplace=True)
    data_mdp.reset_index(drop=True, inplace=True)

    # избавляемся от пропусков в столбце name
    data_mp.dropna(subset=['name'], inplace=True)
    data_mp.reset_index(drop=True, inplace=True)

    data_mp_name = data_mp[['id', 'name']]

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
        df.loc[:, name + '_tok'] = name_tok
        return df

    # функция tokenize для данных от производителя
    tokenize(data_mp_name, 'name')

    data_mp_id = data_mp_name.loc[:, ['id', 'name_tok']]
    data_mp_name.drop(['name', 'id'], axis=1, inplace=True)

    tfIdfVectorizer = TfidfVectorizer(use_idf=True)

    # векторизация данных производителя
    tfIdf = tfIdfVectorizer.fit_transform(data_mp_name['name_tok'])

    # функция tokenize для данных от дилеров
    tokenize(data_mdp, 'product_name')

    # векторизация данных от дилеров
    tfidf_test = tfIdfVectorizer.transform(data_mdp['product_name_tok'])

    # рассчёт расстояний
    res = cdist(tfidf_test.toarray(), tfIdf.toarray(), metric='euclidean')

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

    return model


def matching_predict(lst_dict_pr, lst_dict_tst, model, k=5):
    """
    ФУНКЦИЯ ДЛЯ ПРЕДСКАЗАНИЯ
    -lst_dict_pr список словарей карточек производителей
    -lst_dict_tst список словарей карточек диллеров для предсказания
    -model обученная модель
    -k колличество выводимых id товаров производителя
    для каждой карточки диллера (по умолчанию равно 5)
    """

    data_mdp_test = pd.DataFrame(lst_dict_tst)
    data_mp = pd.DataFrame(lst_dict_pr)

    # избавляемся от пропусков в столбце name
    # в данных производителя
    data_mp.dropna(subset=['name'], inplace=True)
    data_mp.reset_index(drop=True, inplace=True)

    data_mp_name = data_mp[['id', 'name']]

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
    tokenize(data_mp_name, 'name')

    data_mp_id = data_mp_name.loc[:, ['id', 'name_tok']]
    data_mp_name.drop(['name', 'id'], axis=1, inplace=True)

    tfIdfVectorizer = TfidfVectorizer(use_idf=True)

    # векторизация данных производителя
    tfIdf = tfIdfVectorizer.fit_transform(data_mp_name['name_tok'])

    # функция tokenize для данных от дилеров
    tokenize(data_mdp_test, 'product_name')

    # векторизация данных от дилеров
    tfidf_test_t = tfIdfVectorizer.transform(
        data_mdp_test['product_name_tok'])

    # расчёт расстояний
    res_t = cdist(tfidf_test_t.toarray(),
                  tfIdf.toarray(),
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

    # предсказание для теста (данных от дилеров)
    y_pred_all = model.predict(
        res_sort_t,
        num_iteration=model.best_iteration)

    # выделение k самых вероятных объектов из
    # данных производителя для каждой строки дилера
    df_ind_all = pd.DataFrame(
        [np.argsort(y_pred_all[i])[-1: -(k+1): -1] for i in
         range(y_pred_all.shape[0])])

    # итоговый фрэйм с k самых вероятных id
    result = pd.DataFrame(
        [[df_res_lm_t.loc[i, df_ind_all.loc[i, :][j]]
          for j in range(k)] for i in range(df_ind_all.shape[0])])
    result.columns = [str(i) for i in range(1, k+1)]

    res_k = result.to_dict('records')

    return res_k
