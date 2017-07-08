import json

import requests
from django.conf import settings
from urban.celery import app

from urban.apps.articles import models as article_models
from celery import Celery


@app.task
def get_top_articles(number_of_tries=1):
    """
    Get the top articles from the HN api and update the system
    :param number_of_tries: (int) Represents the number of tries
    :return: (None|dict) Represents whether the request was succesfull or not
    """
    if number_of_tries > 3:
        return {
            u'success': False,
            u'error': u'Tried 3 tried but no response'
        }
    try:
        response = requests.get(settings.TOP_ARTICLES_URL, headers=settings.BASE_HEADERS)
    # When the request resulted in a timeout
    except requests.exceptions.Timeout:
        return get_top_articles(number_of_tries=number_of_tries+1)
    else:
        # In case the response is not 200
        if response.status_code != requests.codes.ok:
            return {
                u'success': False,
                u'error': u'Got the response: {}'.format(response.content)
            }
        else:
            list_of_article_ids = json.loads(response.content)
            # Check for the articles which has been in the system
            existing_article_ids = set(article_models.Article.objects.filter(article_id__in=list_of_article_ids).values_list(u'article_id', flat=True))
            new_article_ids = set(list_of_article_ids) - existing_article_ids
            # Trigger get_new_articles in order to update each article in the system
            get_new_articles(article_id_list=list(new_article_ids))


@app.task
def get_new_articles(article_id_list):
    """
    Get the details of new article id 
    :param article_id_list: (list) List of article ids
    :return: (dict) Containing invalid article ids for which the response wasn't 200
    """
    if isinstance(article_id_list, list):

        article_objects = []
        invalid_article_ids = []
        for article_id in article_id_list:
            try:
                response = requests.get(settings.ARTICLE_DETAILS_URL.format(id=article_id), headers=settings.BASE_HEADERS)
            except requests.exceptions.Timeout:
                invalid_article_ids.append(article_id)
            else:
                if response.status_code != requests.codes.ok:
                    invalid_article_ids.append(article_id)
                else:
                    response_data = json.loads(response.content)
                    # Check if an article with the same title exists
                    article_obj = article_models.Article.objects.filter(title=response_data[u'title']).first()
                    if not article_obj:
                        sentiment_obj = get_sentiment_value(title=response_data[u'title'])
                    if not sentiment_obj:
                        continue
                    article_objects.append(
                        article_models.Article(
                            article_id=response_data.get(u'id'),
                            username=response_data.get(u'by'),
                            upvotes=response_data.get(u'score'),
                            title=response_data.get(u'title'),
                            url=response_data.get(u'url'),
                            description=response_data.get(u'text'),
                            sentiment_value=article_obj.sentiment_value if article_obj else sentiment_obj
                        )
                    )
        article_models.Article.objects.bulk_create(article_objects)
        return {
            u'invalid_article_ids': invalid_article_ids,
            u'new_article_objects': len(article_objects)
        }


@app.task
def get_sentiment_value(title=None):
    """
    Get sentiment value 
    :param title: (str) Title
    :return: (object) Sentiment object
    """
    if title:
        try:
            response = requests.post(settings.SENTIMENT_URL, headers=settings.BASE_HEADERS, data={u'txt': title})
        except requests.exceptions.Timeout as e:
            return None
        else:
            if response.status_code != requests.codes.ok:
                return None
            else:
                response_data = json.loads(response.content)
                value = response_data[u'result'][u'sentiment']
                confidence = response_data[u'result'][u'confidence']
                try:
                    sentiment_obj = article_models.Sentiment.objects.get(value=value, confidence=confidence)
                except article_models.Sentiment.DoesNotExist:
                    sentiment_obj = article_models.Sentiment.objects.create(value=value, confidence=confidence)
                return sentiment_obj
