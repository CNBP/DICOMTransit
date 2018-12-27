from redcap.query import redcap_query
import development as environment

def post_cnn_admission(messsage):
    """
    Post a message to the CNN Admission Table GROUP in RedCap
    :param messsage:
    :return:
    """
    token = environment.REDCAP_TOKEN_CNN_ADMISSION
    redcap_query.post(token, messsage)


def post_cnn_baby(messsage):
    """
    Post a message to the CNN Baby Table GROUP in RedCap
    :param messsage:
    :return:
    """
    token = environment.REDCAP_TOKEN_CNN_BABY
    redcap_query.post(token, messsage)


def post_cnn_mother(messsage):
    """
    Post a message to the CNN MOTHER Table GROUP in RedCap
    :param messsage:
    :return:
    """
    token = environment.REDCAP_TOKEN_CNN_MOTHER
    redcap_query.post(token, messsage)


def post_cnn_master(messsage):
    """
    Post a message to the CNN Master Table GROUP in RedCap
    :param messsage:
    :return:
    """
    token = environment.REDCAP_TOKEN_CNN_MASTER
    redcap_query.post(token, messsage)


def post_cnfun_patient(messsage):
    """
    Post a message to the CNFUN Patient Table GROUP in RedCap
    :param messsage:
    :return:
    """
    token = environment.REDCAP_TOKEN_CNFUN_PATIENT
    redcap_query.post(token, messsage)


