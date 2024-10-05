from datastorage.consts import Code

STATUSES = [
    {
        'name': 'Системная категория',
        'code': Code.SYSTEM_CATEGORY,
    },
    {
        'name': 'Категория выбрана',
        'code': Code.CATEGORY_SELECTED,
    },
    {
        'name': 'На рассмотрении',
        'code': Code.ON_CONSIDERATION,
    },
    {
        'name': 'Голос отдан',
        'code': Code.VOTED,
    },
    {
        'name': 'Заявка одобрена',
        'code': Code.REQUEST_SUCCESSFUL,
    },
    {
        'name': 'Участник сообщества',
        'code': Code.COMMUNITY_MEMBER,
    },
    {
        'name': 'Голос по умолчанию',
        'code': Code.VOTED_BY_DEFAULT,
    },
    {
        'name': 'Заявка отозвана',
        'code': Code.REQUEST_EXCLUDED,
    },
]
