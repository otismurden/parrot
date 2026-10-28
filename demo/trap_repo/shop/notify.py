from shop.mailer import Mailer


def notify(user, text):
    Mailer().send_email(user.email, text)
