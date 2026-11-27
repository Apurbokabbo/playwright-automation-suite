from locators.common_locators import CommonLocators


class LoginPageLocators(CommonLocators):

    EMAIL_FIELD_PLACEHOLDER_TEXT = "Email Address"
    PASSWORD_FIELD_PLACEHOLDER_TEXT = "Password"
    LOGIN_MODAL_TITTLE_TEXT = "Login to your account"


    LOGIN_MODAL_TITTLE_TEXT_LOCATOR="//section[@id='form']//h2[normalize-space(.)='Login to your account']"
    EMAIL_FIELD_INPUT_FIELD ="[data-qa='login-email']"
    PASSWORD_FIELD_INPUT_FIELD ="[data-qa='login-password']"
    LOGIN_BUTTON ="[data-qa='login-button']"




class SignUpPageLocators:

    NAME_FIELD_PLACEHOLDER_TEXT = "Name"
    SIGNUP_MODAL_TITTLE_TEXT="New User Signup!"


    SIGNUP_MODAL_TITTLE_TEXT_LOCATOR="//section[@id='form']//h2[normalize-space(.)='New User Signup!']"
    EMAIL_FIELD_INPUT_FIELD = "[data-qa='signup-email']"
    NAME_FIELD_INPUT_FIELD = "[data-qa='signup-name']"
    SIGNUP_BUTTON="[data-qa='signup-button']"

