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
        'name': 'Голос не отдан',
        'code': Code.ABSTAINED,
    },
    {
        'name': 'Заявка одобрена',
        'code': Code.REQUEST_SUCCESSFUL,
    },
    {
        'name': 'Заявка отклонена',
        'code': Code.REQUEST_DENIED,
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
        'name': 'Участник исключён',
        'code': Code.MEMBER_EXCLUDED,
    },
    {
        'name': 'Получено принципиальное согласие',
        'code': Code.PRINCIPAL_AGREEMENT,
    },
    {
        'name': 'Необходим компромисс',
        'code': Code.COMPROMISE,
    },
    {
        'name': 'Вступило в силу',
        'code': Code.RULE_APPROVED,
    },
    {
        'name': 'Правило отменено',
        'code': Code.RULE_REVOKED,
    },
    {
        'name': 'Выбор последствий несоблюдения правила',
        'code': Code.NONCOMPLIANCE,
    },
    {
        'name': 'Инициатива одобрена',
        'code': Code.INITIATIVE_APPROVED,
    },
    {
        'name': 'Инициатива отменена',
        'code': Code.INITIATIVE_REVOKED,
    },
    {
        'name': 'Событие завершено',
        'code': Code.EVENT_COMPLETED,
    },
]
