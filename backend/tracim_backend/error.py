# Error code format
# 1xxx: not found error
# 2xxx: validation error
# 3xxx: conflict error
# 4xxx: authentication and authorization
# 9xxx: core errors(family of error code reserved
# for unclassable errors or very low level errors)


# Tracim Not found Error
ERROR_CODE_USER_NOT_FOUND = '1001'
ERROR_CODE_WORKSPACE_NOT_FOUND = '1002'
ERROR_CODE_CONTENT_NOT_FOUND = '1003'
ERROR_CODE_PARENT_NOT_FOUND = '1004'
# Preview Based
ERROR_CODE_UNAVAILABLE_PREVIEW_TYPE = '1011'
ERROR_CODE_PAGE_OF_PREVIEW_NOT_FOUND = '1012'
ERROR_CODE_UNAIVALABLE_PREVIEW = '1013'

# Validation Error
ERROR_CODE_GENERIC_SCHEMA_VALIDATION_ERROR = '2001'
# Not in Tracim Request #
ERROR_CODE_USER_NOT_IN_TRACIM_REQUEST = '2011'
ERROR_CODE_WORKSPACE_NOT_IN_TRACIM_REQUEST = '2012'
ERROR_CODE_CONTENT_NOT_IN_TRACIM_REQUEST = '2013'
# Invalid ID #
ERROR_CODE_USER_INVALID_USER_ID = '2021'
ERROR_CODE_WORKSPACE_INVALID_ID = '2022'
ERROR_CODE_CONTENT_INVALID_ID = '2023'
ERROR_CODE_COMMENT_INVALID_ID = '2024'

# Other #
ERROR_CODE_CONTENT_TYPE_NOT_ALLOWED = '2031'
ERROR_CODE_WORKSPACE_DO_NOT_MATCH = '2032'
ERROR_CODE_PREVIEW_DIM_NOT_ALLOWED = '2033'
ERROR_CODE_WRONG_USER_PASSWORD = '2034'
ERROR_CODE_PASSWORD_DO_NOT_MATCH = '2035'
ERROR_CODE_EMAIL_ALREADY_EXIST_IN_DB = '2036'
ERROR_CODE_EMAIL_VALIDATION_FAILED = '2037'
ERROR_CODE_EMAIL_UNALLOWED_SUBCONTENT = '2038'
ERROR_CODE_INVALID_RESET_PASSWORD_TOKEN = '2039'
ERROR_CODE_EXPIRED_RESET_PASSWORD_TOKEN = '2040'
ERROR_CODE_SAME_VALUE_ERROR = '2041'

# Conflict Error
ERROR_CODE_USER_ALREADY_EXIST = '3001'
ERROR_CODE_CONTENT_LABEL_ALREADY_USED_THERE = '3002'

# Auth Error
ERROR_CODE_AUTHENTICATION_FAILED = '4001'
# Right Error
ERROR_CODE_INSUFFICIENT_USER_PROFILE = '4002'
ERROR_CODE_INSUFFICIENT_USER_ROLE_IN_WORKSPACE = '4003'
