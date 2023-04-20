from requests import get, codes, post

from settings import SiteSettings

site = SiteSettings()

"""
Универсальная функция, которая делает запросы к API, а в дочерних функциях обрабатываются результаты ответа
"""


def api_request(method_endswith: str, params: dict, method_type: str,
                your_param: int = 0) -> dict | list | list[tuple[str, dict]]:
    """
    method_endswith - меняется в зависимости от запроса. locations/v3/search или properties/v2/list
    params - параметры, если locations/v3/search, то {'q': 'Рига', 'locale': 'ru_RU'}
    Тип запроса GET или POST
    your_param по дефолту установлен на 0, дальше принимает значение int от пользователя
    """

    url = f"https://{site.host_api}/{method_endswith}"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": site.api_key.get_secret_value(),
        "X-RapidAPI-Host": site.host_api
    }
    """В зависимости от типа запроса вызываем соответствующую функцию"""
    if method_type == 'GET':
        return get_request(
            url=url,
            params=params,
            headers=headers,
        )

    else:
        return post_request(
            url=url,
            params=params,
            headers=headers,
            your_param=your_param,
        )


def get_request(url: str, params: dict, headers: dict) -> dict:
    """
    Получаем название городов по запросу от пользователя
    """
    city_list = {}
    try:
        response = get(
            url=url,
            headers=headers,
            params=params,
            timeout=15
        )

        if response.status_code == codes.ok:
            city_response = response.json()

            for i in city_response['sr']:
                if i['type'] == 'CITY':
                    city_list[i['regionNames']['fullName']] = i['essId']['sourceId']
            return city_list
    except:
        return city_list


def post_request(url: str, params: dict, headers: dict, your_param: int) -> list | list[tuple[str, dict]]:
    response = post(
        url=url,
        json=params,
        headers=headers,
        timeout=30
    )

    if response.status_code == codes.ok:
        if url == 'https://hotels4.p.rapidapi.com/properties/v2/get-summary':
            response = post(url, json=params, headers=headers)
            dict_foto = response.json()
            foto_hotel = [foto['image']['url'] for foto in
                          dict_foto['data']['propertyInfo']['propertyGallery']['images']]
            return foto_hotel
        else:
            dict_hotel = response.json()
            hotel_list = []

            for i, hotel in enumerate(dict_hotel["data"]['propertySearch']['properties']):
                foto = api_request(
                    method_endswith='properties/v2/get-summary',
                    params={"currency": "USD",
                            "eapid": 1,
                            "locale": "ru_RU",
                            "siteId": 300000001,
                            "propertyId": str(hotel['id'])},
                    method_type='POST',
                )
                hotel_name = hotel['name']
                distance = hotel['destinationInfo']['distanceFromDestination']['unit'], \
                    hotel['destinationInfo']['distanceFromDestination']['value']
                total_price = hotel['price']['displayMessages'][1]['lineItems'][0]['value']
                price_min = hotel['price']['options'][int('0')]['formattedDisplayPrice']
                hotel_list.append((f"Отель: {hotel_name}\n"
                                   f"Расстояние от центра - {distance}\n"
                                   f"Минимальна ценна - {price_min}\n"
                                   f"Итоговая стоимость - {total_price}\n"
                                   f"https://www.hotels.com/h{hotel['id']}.Hotel-Information", foto))
                if i == int(your_param) - 1:
                    return hotel_list