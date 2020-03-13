
import os
import boto.s3.connection

class Env:
    __evn_dist = os.environ

    @staticmethod
    def judge_env(env, message):
        env_value = Env.__evn_dist.get(env)
        if env_value is None:
            raise RuntimeError(message + env)

        return env_value


class ConnectS3(object):
    def __init__(self):
        self.conn = boto.connect_s3(
            aws_access_key_id = Env.judge_env("S3_ACCESS_KEY", "s3_access_key"),
            aws_secret_access_key = Env.judge_env("S3_SECRET_KEY", "s3_secret_key"),
                host = Env.judge_env("S3_HOST", "s3_host"),
            port = int(Env.judge_env("S3_PORT", "s3_port")),
            is_secure=False,  # uncomment if you are not using ssl
            calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )

        self.model_key = Env.judge_env("MODEL_KEY", "model_key")
        self.network_key = Env.judge_env("NETWORK_KEY", "network_key")
        try:
            self.transform_key = Env.judge_env("TRANSFORM_KEY", "transform_key")
        except:
            self.transform_key = None

        self.bucket = self.conn.get_bucket(Env.judge_env("BUCKET", "bucket"))

        # get Transform.py
        self.set_transform(self.transform_key)

        model_type = Env.judge_env("MODEL_TYPE", "model_type")
        if model_type == "PT":
            self.set_pt()

        # get model data
        self.set_model_data()

    def set_model_data(self):
        key = self.bucket.get_key(self.model_key)
        key.get_contents_to_filename("./model.m")

    def set_pt(self):
        key = self.bucket.get_key(self.network_key)
        key.get_contents_to_filename("./network.py")

    def set_transform(self, transform_key):
        if not transform_key is None:
            key = self.bucket.get_key(transform_key)
            key.get_contents_to_filename("./transform.py")

    def get_version(self):
        key_path = self.network_key.split("/")
        if len(key_path) > 1:
            return key_path[1]

        return None

    def get_transform_key(self):
        return self.transform_key

#s3 = ConnectS3('kubeflow-anonymous-test', "test/2019-12-16T15-47-38Z/test", None,'test/2019-12-16T17-43-41Z/network')