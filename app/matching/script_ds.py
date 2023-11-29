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


def match(lst_dict_pr, lst_dict_dr, lst_dict_k, lst_dict_tst=None):
    """
    -lst_dict_pr список словарей карточек производителя
    -lst_dict_dr список словарей карточек дилеров для обучения
                        (существующие данные из marketing_dealerprice.csv
                        к примеру, то есть с разметкой)
    -lst_dict_k список словарей внешних ключей
    -lst_dict_tst список словарей карточек диллеров для предсказания
                        (можно те же данные из lst_dict_dr);
                        по умолчанию None, то есть предсказываются id
                        карточек дилеров из lst_dict_dr (дынных для обучения)
    """

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

        test_null = data_mdp.merge(data_mpdk,
                                   how='left',
                                   left_on='product_key',
                                   right_on='key').loc[:, ['product_key',
                                                           'key',
                                                           'product_id']]

        ind_drop = test_null.loc[test_null['product_id'].isnull()].index.values
        data_mdp.drop(ind_drop, axis=0, inplace=True)
        data_mdp.reset_index(drop=True, inplace=True)

        data_mp.dropna(subset=['name'], inplace=True)
        # избавляемся от пропусков в столбце name

        data_mp.reset_index(drop=True, inplace=True)

        data_mp_name = data_mp[['id', 'name']]

        tokenize(data_mp_name, 'name')
        # функция tokenize для данных от производителя

        data_mp_id = data_mp_name.loc[:, ['id', 'name_tok']]
        data_mp_name.drop(['name', 'id'], axis=1, inplace=True)

        tfIdfVectorizer = TfidfVectorizer(use_idf=True)
        tfIdf = tfIdfVectorizer.fit_transform(data_mp_name['name_tok'])
        # векторизация данных производителя

        tokenize(data_mdp, 'product_name')
        # функция tokenize для данных от дилеров

        tfidf_test = tfIdfVectorizer.transform(data_mdp['product_name_tok'])
        # векторизация данных от дилеров

        res = cdist(tfidf_test.toarray(), tfIdf.toarray(), metric='euclidean')
        # рассчёт расстояний

        res = pd.DataFrame(res)
        res_sort = pd.DataFrame([np.sort(res.iloc[i, :]) for i in
                                 range(res.shape[0])])
        # сортировка расстояний

        res_lm = pd.DataFrame(
            [np.argsort(res.iloc[i, :]) for i in range(res.shape[0])])

        # фрэйм отсортированных расстояний в значениях id

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

        for j in range(testlm.shape[0]):
            df_res_lm.loc[j, :] = np.where(
                df_res_lm.loc[j, :].values == testlm.loc[
                    j, 'product_id'], 1, 0)
        # заполнение 0 и 1 фрэйма с id, где 1 означает верный id

        for j in range(df_res_lm.shape[0]):
            df_res_lm.loc[j, 'target'] = (df_res_lm.loc[j, :].
                                          values.
                                          tolist().
                                          index(1))
        # целевая переменная, номер столбца, в котором стоит 1,
        # то есть верного id в отсортированном фрэйме

        X_train, X_test, Y_train, Y_test = train_test_split(res_sort,
                                                            df_res_lm.target)
        # разделение данных с отсортированными
        # значениями расстояний на выборки для обучения модели

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

        num_round = 100
        model = lgb.train(params,
                          train_data,
                          num_round,
                          valid_sets=[valid_data])
        # обучение модели LGBM для мультиклассовой классификации

        return model

    model = matching_training(lst_dict_pr, lst_dict_dr, lst_dict_k)
    # ОБУЧЕННАЯ МОДЕЛЬ

    def matching_predict(lst_dict_pr, lst_dict_tst, model):
        """
        ФУНКЦИЯ ДЛЯ ПРЕДСКАЗАНИЯ
        -lst_dict_pr список словарей карточек производителей
        -lst_dict_tst список словарей карточек диллеров для предсказания
        -model обученная модель
        """

        if not lst_dict_tst:
            # если по умолчанию, то предсказываются
            # id для карточек дилеров из обучающего фрэйма,
            # иначе - для новых данных
            lst_dict_tst = lst_dict_dr
        data_mdp_test = pd.DataFrame(lst_dict_tst)
        data_mp = pd.DataFrame(lst_dict_pr)

        data_mp.dropna(subset=['name'], inplace=True)
        # избавляемся от пропусков в столбце name

        data_mp.reset_index(drop=True, inplace=True)

        data_mp_name = data_mp[['id', 'name']]

        tokenize(data_mp_name, 'name')
        # функция tokenize для данных от производителя

        data_mp_id = data_mp_name.loc[:, ['id', 'name_tok']]
        data_mp_name.drop(['name', 'id'], axis=1, inplace=True)

        tfIdfVectorizer = TfidfVectorizer(use_idf=True)
        tfIdf = tfIdfVectorizer.fit_transform(data_mp_name['name_tok'])
        # векторизация данных производителя
        # подготовка данных для теста

        tokenize(data_mdp_test, 'product_name')
        # функция tokenize для данных от дилеров

        tfidf_test_t = tfIdfVectorizer.transform(
            data_mdp_test['product_name_tok'])
        # векторизация данных от дилеров

        res_t = cdist(
            tfidf_test_t.toarray(),
            tfIdf.toarray(),
            metric='euclidean')
        # расчёт расстояний

        res_t = pd.DataFrame(res_t)
        res_sort_t = pd.DataFrame(
            [np.sort(res_t.iloc[i, :]) for i in range(res_t.shape[0])])
        res_lm_t = pd.DataFrame(
            [np.argsort(res_t.iloc[i, :]) for i in range(res_t.shape[0])])
        # фрэйм отсортированных расстояний

        df_res_lm_t = pd.DataFrame(
            [[data_mp_id.loc[i, 'id'] for i in res_lm_t.loc[j, :]] for j in
             range(res_lm_t.shape[0])])
        # предсказание для теста(полных данных от дилеров)

        y_pred_all = model.predict(
            res_sort_t,
            num_iteration=model.best_iteration)

        df_ind_all = pd.DataFrame(
            [np.argsort(y_pred_all[i])[-1: -6: -1] for i in
             range(y_pred_all.shape[0])])
        # выделение 5 самых вероятных объектов из
        # данных производителя для каждой строки дилера

        result = pd.DataFrame(
            [[df_res_lm_t.loc[i, df_ind_all.loc[i, :][j]]
              for j in range(5)] for i in range(df_ind_all.shape[0])]
        )
        result.columns = ['1', '2', '3', '4', '5']
        # итоговый фрэйм с 5 самых вероятных id

        res_5 = result.to_dict('records')

        return res_5

    res = matching_predict(lst_dict_pr, lst_dict_tst, model)
    return res
