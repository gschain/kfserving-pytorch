import kfserving
from typing import List, Dict
import logging
import torch
import transform
import network
from importlib import reload
from connect_s3 import Env
import connect_s3


logging.basicConfig(level=kfserving.constants.KFSERVING_LOGLEVEL)

class KfservingPytorch(kfserving.KFModel):

    __loaded = False
    __model = None
    __version = None

    def __init__(self, name: str):
        super().__init__(name)
        logging.info("Initializing...")
        self.s3 = connect_s3.ConnectS3()
        transform_key = self.s3.get_transform_key()
        if not transform_key is None:
            logging.info("transform key:" + transform_key)
            reload(transform)

        self.__version = self.s3.get_version()
        reload(network)
        self.load_model()

    def load_model(self):
        logging.info("start load model")
        self.__model = torch.load('./model.m', map_location=torch.device('cpu'))
        logging.info("model loaded")
        self.__loaded = True

    def predict(self, request: Dict) -> Dict:
        if not self.__loaded:
            self.load_model()

        if 'ndarray' not in request:
            logging.info("request json error!")
            return "request json error!"

        if self.__model:
            transform_obj = transform.Transform()
            transform_obj.transform_input(request['ndarray'])
            result_dict = transform_obj.transform_output(self.__model)
            result_dict['version'] = self.__version
            return result_dict
        else:
            return None


if __name__ == "__main__":
    model = KfservingPytorch("kfserving-pytorch")
    try:
        workers = int(Env.judge_env("WORKERS", "workers"))
    except():
        workers = 1
    kfserving.KFServer(workers=workers).start([model])