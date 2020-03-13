import numpy as np
import torch

class Transform(object):

    def transform_input(self, X):
        # parse parameters
        self.request_size = int(X[0])
        self.base_size = int(X[1])
        self.base_values = X[2]
        self.feature_size = int(X[3])
        self.feature_values = X[4]
        flag = False
        msg = None

        self.base_values = np.array(self.base_values)
        self.feature_values = np.array(self.feature_values)

        if self.base_values.size != self.base_size:
            flag = True
            msg = 'baseSize check failure'

        if self.feature_values.size != self.feature_size:
            flag = True
            msg = 'featureSize check failure'

        if flag:
            return "parameter error %s" % msg

    def transform_output(self, model):
        new_array = self.generate_array(self.base_size, self.base_values, self.feature_size, self.feature_values)
        x1, x2 = self.generate_torch_data(new_array)
        t0 = torch.tensor(x1)
        t1 = torch.tensor(x2)
        result = torch.sigmoid(model(t0, t1)).data
        result = self.deal_result(result.numpy())

        result_dict = {}
        result_dict['ndarray'] = result

        return result_dict

    def generate_array(self, base_size, base_values, feature_size, feature_values):
        new_arry = np.zeros((feature_size, base_size))
        for i in range(feature_size):
            new_arry[i] = base_values

        return np.insert(new_arry, 1, feature_values, axis=1)

    def generate_torch_data(self, new_array):
        xi = []
        xv = []

        for size in range(self.feature_size):
            t1, t2 = self.trans(new_array[size])
            xi.append(t1)
            xv.append(t2)

        xi = np.array(xi)
        xv = np.array(xv)
        return xi, xv

    def trans(self, aim58):
        t1 = aim58[0:8]
        xi = np.array([ [t1[0]], [t1[1]], [t1[2]], [t1[3]], [t1[4]], [t1[5]], [t1[6]], [t1[7]] ], dtype='long')
        t2_head = [1, 1, 1, 1, 1, 1, 1, 1 ]
        xv = np.array(t2_head + list(aim58[8:]), dtype='float32')
        return (xi, xv)

    def deal_result(self, result):
        result_dict = {}
        for i in range(self.feature_size):
            result_dict[self.feature_values[i]] = result[i]

        #result_dict = sorted(dict.items(), key=lambda x: x[1], reverse=True)
        size = len(result_dict)
        if self.request_size < size:
            result_dict = dict(list(result_dict.items())[:self.request_size])

        #return json.dumps(self.aggregation_json(result_dict), cls=NpEncoder)
        #json.dumps(self.aggregation_json(result_dict))
        return self.aggregation_json(result_dict)

    def aggregation_json(self, result_dict):
        item_list = []
        for (k, v) in result_dict.items():
            item_dict = {}
            item_dict["id"] = int(k)
            item_dict["score"] = float(v)
            item_list.append(item_dict)

        return item_list