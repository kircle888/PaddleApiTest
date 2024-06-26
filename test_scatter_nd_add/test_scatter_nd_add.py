import sys
import unittest

import numpy as np

import paddle
from paddle.utils import map_structure
import functools 

sys.path.append("..")
from utils import (
    TOLERANCE,
    convert_dtype_to_torch_type,
    np_assert_accuracy,
    np_assert_staility,
)

def numpy_scatter_nd(ref, index, updates, fun):
    ref_shape = ref.shape
    index_shape = index.shape

    end_size = index_shape[-1]
    remain_numel = 1
    for i in range(len(index_shape) - 1):
        remain_numel *= index_shape[i]

    slice_size = 1
    for i in range(end_size, len(ref_shape)):
        slice_size *= ref_shape[i]

    flat_index = index.reshape([remain_numel] + list(index_shape[-1:]))
    flat_updates = updates.reshape((remain_numel, slice_size))
    flat_output = ref.reshape(list(ref_shape[:end_size]) + [slice_size])

    for i_up, i_out in enumerate(flat_index):
        i_out = tuple(i_out)
        flat_output[i_out] = fun(flat_output[i_out], flat_updates[i_up])
    return flat_output.reshape(ref.shape)


def numpy_scatter_nd_add(ref, index, updates):
    return numpy_scatter_nd(ref, index, updates, lambda x, y: x + y)


def judge_update_shape(ref, index):
    ref_shape = ref.shape
    index_shape = index.shape
    update_shape = []
    for i in range(len(index_shape) - 1):
        update_shape.append(index_shape[i])
    for i in range(index_shape[-1], len(ref_shape), 1):
        update_shape.append(ref_shape[i])
    return update_shape

def expand_class(shapes, dtypes):
    def decorate(cls):
        test_cls_module = sys.modules[cls.__module__].__dict__
        unittest_num = 1
        for shape in shapes:
            for dtype in dtypes:
                test_cls = dict(cls.__dict__)
                test_cls["shapes"] = shape
                test_cls["dtype"] = dtype
                name = cls.__name__ + str(unittest_num)
                unittest_num += 1
                test_cls_module[name] = type(name, (cls,), test_cls)

        for m in list(cls.__dict__):
            if m.startswith("test"):
                delattr(cls, m)
        return cls

    return decorate

shape_all = [[[1, 1056, 2048],[1024, 2],[1024, 2048]],[[1, 54],[1, 2],[1]],[[1, 2745],[1024, 2],[1024]],[[1, 1038, 2048],[1024, 2],[1024, 2048]],[[1, 1048],[1024, 2],[1024]],[[1, 24],[1, 2],[1]],[[1, 3041],[1024, 2],[1024]],[[1, 21],[1, 2],[1]],[[1, 12],[1, 2],[1]],[[1, 23],[1, 2],[1]],[[1264],[1, 1],[1]],[[1, 1045, 2048],[1024, 2],[1024, 2048]],[[1, 18],[1, 2],[1]],[[28],[1, 1],[1]],[[13],[1, 1],[1]],[[1, 1078, 2048],[1024, 2],[1024, 2048]],[[1, 20],[1, 2],[1]],[[1, 1070, 2048],[1024, 2],[1024, 2048]],[[1316],[1, 1],[1]],[[1, 2339],[1024, 2],[1024]],[[1, 1063, 2048],[1024, 2],[1024, 2048]],[[27],[1, 1],[1]],[[1, 1081, 2048],[1024, 2],[1024, 2048]],[[1, 1077],[1024, 2],[1024]],[[17],[1, 1],[1]],[[1, 1061],[1024, 2],[1024]],[[1, 2287, 2048],[1024, 2],[1024, 2048]],[[1, 1060],[1024, 2],[1024]],[[47],[1, 1],[1]],[[1, 1316],[1, 2],[1]],[[39],[1, 1],[1]],[[38],[1, 1],[1]],[[1, 39],[1, 2],[1]],[[1, 1046, 2048],[1024, 2],[1024, 2048]],[[1, 1051],[1024, 2],[1024]],[[1, 1036, 2048],[1024, 2],[1024, 2048]],[[1, 1063],[1024, 2],[1024]],[[1, 1051, 2048],[1024, 2],[1024, 2048]],[[1, 27],[1, 2],[1]],[[1, 1047],[1024, 2],[1024]],[[58],[1, 1],[1]],[[1, 34],[1, 2],[1]],[[1, 1038],[1024, 2],[1024]],[[1, 1040],[1024, 2],[1024]],[[1, 55],[1, 2],[1]],[[1, 1067],[1024, 2],[1024]],[[1, 2745, 2048],[1024, 2],[1024, 2048]],[[14],[1, 1],[1]],[[1, 14],[1, 2],[1]],[[1, 2913],[1024, 2],[1024]],[[1, 2983, 2048],[1024, 2],[1024, 2048]],[[1, 1034],[1024, 2],[1024]],[[1, 1059],[1024, 2],[1024]],[[32],[1, 1],[1]],[[1, 1932],[1, 2],[1]],[[34],[1, 1],[1]],[[36],[1, 1],[1]],[[1354],[1, 1],[1]],[[1, 1072, 2048],[1024, 2],[1024, 2048]],[[1, 1043, 2048],[1024, 2],[1024, 2048]],[[1, 1058],[1024, 2],[1024]],[[20],[1, 1],[1]],[[1, 37],[1, 2],[1]],[[1, 1066],[1024, 2],[1024]],[[1, 1052],[1024, 2],[1024]],[[1, 38],[1, 2],[1]],[[26],[1, 1],[1]],[[1, 1053],[1024, 2],[1024]],[[1, 1062],[1024, 2],[1024]],[[48],[1, 1],[1]],[[1722],[1, 1],[1]],[[1, 33],[1, 2],[1]],[[1, 1059, 2048],[1024, 2],[1024, 2048]],[[1, 1054],[1024, 2],[1024]],[[1, 1061, 2048],[1024, 2],[1024, 2048]],[[1, 28],[1, 2],[1]],[[1, 1041, 2048],[1024, 2],[1024, 2048]],[[1, 1047, 2048],[1024, 2],[1024, 2048]],[[1, 1045],[1024, 2],[1024]],[[1, 1034, 2048],[1024, 2],[1024, 2048]],[[1, 2983],[1024, 2],[1024]],[[18],[1, 1],[1]],[[1, 1046],[1024, 2],[1024]],[[1, 1043],[1024, 2],[1024]],[[1, 25],[1, 2],[1]],[[35],[1, 1],[1]],[[1, 22],[1, 2],[1]],[[1, 1071, 2048],[1024, 2],[1024, 2048]],[[1, 1054, 2048],[1024, 2],[1024, 2048]],[[1, 1053, 2048],[1024, 2],[1024, 2048]],[[1, 1722],[1, 2],[1]],[[29],[1, 1],[1]],[[1, 1042, 2048],[1024, 2],[1024, 2048]],[[2018],[1, 1],[1]],[[37],[1, 1],[1]],[[1, 1041],[1024, 2],[1024]],[[1, 58],[1, 2],[1]],[[1, 1050],[1024, 2],[1024]],[[1, 2339, 2048],[1024, 2],[1024, 2048]],[[55],[1, 1],[1]],[[1, 1037, 2048],[1024, 2],[1024, 2048]],[[31],[1, 1],[1]],[[33],[1, 1],[1]],[[43],[1, 1],[1]],[[1, 1050, 2048],[1024, 2],[1024, 2048]],[[1, 35],[1, 2],[1]],[[1932],[1, 1],[1]],[[1, 49],[1, 2],[1]],[[44],[1, 1],[1]],[[22],[1, 1],[1]],[[1, 1039, 2048],[1024, 2],[1024, 2048]],[[1, 1036],[1024, 2],[1024]],[[1, 1078],[1024, 2],[1024]],[[1960],[1, 1],[1]],[[1, 1049, 2048],[1024, 2],[1024, 2048]],[[1, 40],[1, 2],[1]],[[1, 2955],[1024, 2],[1024]],[[1, 1044],[1024, 2],[1024]],[[1, 43],[1, 2],[1]],[[1, 1039],[1024, 2],[1024]],[[1, 13],[1, 2],[1]],[[1, 1077, 2048],[1024, 2],[1024, 2048]],[[1, 1035],[1024, 2],[1024]],[[1, 2287],[1024, 2],[1024]],[[1, 2955, 2048],[1024, 2],[1024, 2048]],[[1, 19],[1, 2],[1]],[[25],[1, 1],[1]],[[49],[1, 1],[1]],[[16],[1, 1],[1]],[[1, 1890],[1, 2],[1]],[[1, 30],[1, 2],[1]],[[19],[1, 1],[1]],[[1, 1062, 2048],[1024, 2],[1024, 2048]],[[1, 2018],[1, 2],[1]],[[1, 26],[1, 2],[1]],[[1, 36],[1, 2],[1]],[[1, 1037],[1024, 2],[1024]],[[1, 1035, 2048],[1024, 2],[1024, 2048]],[[23],[1, 1],[1]],[[1, 1070],[1024, 2],[1024]],[[1, 1081],[1024, 2],[1024]],[[1, 15],[1, 2],[1]],[[1, 1066, 2048],[1024, 2],[1024, 2048]],[[1, 3041, 2048],[1024, 2],[1024, 2048]],[[1, 1055, 2048],[1024, 2],[1024, 2048]],[[1, 31],[1, 2],[1]],[[40],[1, 1],[1]],[[1, 1057],[1024, 2],[1024]],[[1, 2913, 2048],[1024, 2],[1024, 2048]],[[21],[1, 1],[1]],[[1, 1060, 2048],[1024, 2],[1024, 2048]],[[1, 1052, 2048],[1024, 2],[1024, 2048]],[[1, 1042],[1024, 2],[1024]],[[1, 17],[1, 2],[1]],[[1, 1049],[1024, 2],[1024]],[[1, 1071],[1024, 2],[1024]],[[1, 1048, 2048],[1024, 2],[1024, 2048]],[[1, 1264],[1, 2],[1]],[[1, 1067, 2048],[1024, 2],[1024, 2048]],[[15],[1, 1],[1]],[[1, 1044, 2048],[1024, 2],[1024, 2048]],[[1, 29],[1, 2],[1]],[[1, 44],[1, 2],[1]],[[1, 1057, 2048],[1024, 2],[1024, 2048]],[[1, 1058, 2048],[1024, 2],[1024, 2048]],[[1, 1354],[1, 2],[1]],[[1, 1040, 2048],[1024, 2],[1024, 2048]],[[24],[1, 1],[1]],[[1, 16],[1, 2],[1]],[[1, 47],[1, 2],[1]],[[1, 2377],[1024, 2],[1024]],[[1, 1072],[1024, 2],[1024]],[[54],[1, 1],[1]],[[11],[1, 1],[1]],[[1, 1960],[1, 2],[1]],[[1, 1055],[1024, 2],[1024]],[[1, 2377, 2048],[1024, 2],[1024, 2048]],[[30],[1, 1],[1]],[[1, 1056],[1024, 2],[1024]],[[1, 32],[1, 2],[1]],[[1890],[1, 1],[1]],[[1, 48],[1, 2],[1]],[[1, 11],[1, 2],[1]],[[12],[1, 1],[1]],[[1, 18],[1, 2],[1]],[[1, 36],[1, 2],[1]],[[1, 1054],[1024, 2],[1024]],[[1, 30],[1, 2],[1]],[[1, 1045, 2048],[1024, 2],[1024, 2048]],[[1, 1038],[1024, 2],[1024]],[[23],[1, 1],[1]],[[1, 1090],[1024, 2],[1024]],[[1, 1069],[1024, 2],[1024]],[[1, 1078],[1024, 2],[1024]],[[1, 32],[1, 2],[1]],[[25],[1, 1],[1]],[[1, 35],[1, 2],[1]],[[1, 1058, 2048],[1024, 2],[1024, 2048]],[[1, 1064],[1024, 2],[1024]],[[1, 38],[1, 2],[1]],[[1, 1036],[1024, 2],[1024]],[[67],[1, 1],[1]],[[1, 1044, 2048],[1024, 2],[1024, 2048]],[[1, 1049],[1024, 2],[1024]],[[1, 13],[1, 2],[1]],[[1, 1099],[1024, 2],[1024]],[[1, 27],[1, 2],[1]],[[1, 1048, 2048],[1024, 2],[1024, 2048]],[[1, 1066],[1024, 2],[1024]],[[1, 1039],[1024, 2],[1024]],[[32],[1, 1],[1]],[[1, 20],[1, 2],[1]],[[1, 1057],[1024, 2],[1024]],[[1, 44],[1, 2],[1]],[[1, 67],[1, 2],[1]],[[1, 1064, 2048],[1024, 2],[1024, 2048]],[[36],[1, 1],[1]],[[1, 1067, 2048],[1024, 2],[1024, 2048]],[[26],[1, 1],[1]],[[1, 76],[1, 2],[1]],[[1, 1042],[1024, 2],[1024]],[[1, 55],[1, 2],[1]],[[1, 1056, 2048],[1024, 2],[1024, 2048]],[[1, 1056],[1024, 2],[1024]],[[1, 54],[1, 2],[1]],[[27],[1, 1],[1]],[[1, 34],[1, 2],[1]],[[41],[1, 1],[1]],[[1, 1046],[1024, 2],[1024]],[[1, 1061],[1024, 2],[1024]],[[1, 1067],[1024, 2],[1024]],[[1, 41],[1, 2],[1]],[[1, 16],[1, 2],[1]],[[1, 24],[1, 2],[1]],[[55],[1, 1],[1]],[[34],[1, 1],[1]],[[1, 48],[1, 2],[1]],[[18],[1, 1],[1]],[[29],[1, 1],[1]],[[20],[1, 1],[1]],[[16],[1, 1],[1]],[[43],[1, 1],[1]],[[24],[1, 1],[1]],[[1, 1054, 2048],[1024, 2],[1024, 2048]],[[1, 1044],[1024, 2],[1024]],[[1, 11],[1, 2],[1]],[[1, 1065, 2048],[1024, 2],[1024, 2048]],[[1, 1379, 2048],[1024, 2],[1024, 2048]],[[1, 1040],[1024, 2],[1024]],[[28],[1, 1],[1]],[[1, 1037, 2048],[1024, 2],[1024, 2048]],[[54],[1, 1],[1]],[[1, 43],[1, 2],[1]],[[33],[1, 1],[1]],[[1, 356],[1, 2],[1]],[[13],[1, 1],[1]],[[1, 1035, 2048],[1024, 2],[1024, 2048]],[[1, 1052],[1024, 2],[1024]],[[1, 1042, 2048],[1024, 2],[1024, 2048]],[[1, 1043],[1024, 2],[1024]],[[1, 21],[1, 2],[1]],[[44],[1, 1],[1]],[[35],[1, 1],[1]],[[1, 1099, 2048],[1024, 2],[1024, 2048]],[[1, 12],[1, 2],[1]],[[1, 1052, 2048],[1024, 2],[1024, 2048]],[[1, 1065],[1024, 2],[1024]],[[1, 1066, 2048],[1024, 2],[1024, 2048]],[[1, 33],[1, 2],[1]],[[14],[1, 1],[1]],[[39],[1, 1],[1]],[[1, 1078, 2048],[1024, 2],[1024, 2048]],[[1, 1048],[1024, 2],[1024]],[[1, 1045],[1024, 2],[1024]],[[1, 42],[1, 2],[1]],[[1, 23],[1, 2],[1]],[[1, 1076, 2048],[1024, 2],[1024, 2048]],[[1, 1041, 2048],[1024, 2],[1024, 2048]],[[1, 1055, 2048],[1024, 2],[1024, 2048]],[[1, 19],[1, 2],[1]],[[1, 14],[1, 2],[1]],[[1, 1062, 2048],[1024, 2],[1024, 2048]],[[1, 1077],[1024, 2],[1024]],[[1, 1062],[1024, 2],[1024]],[[1, 31],[1, 2],[1]],[[19],[1, 1],[1]],[[356],[1, 1],[1]],[[1, 1053, 2048],[1024, 2],[1024, 2048]],[[1, 1071, 2048],[1024, 2],[1024, 2048]],[[17],[1, 1],[1]],[[1, 1090, 2048],[1024, 2],[1024, 2048]],[[1, 1036, 2048],[1024, 2],[1024, 2048]],[[1, 25],[1, 2],[1]],[[1, 1037],[1024, 2],[1024]],[[46],[1, 1],[1]],[[1, 15],[1, 2],[1]],[[1, 1046, 2048],[1024, 2],[1024, 2048]],[[1, 1050],[1024, 2],[1024]],[[48],[1, 1],[1]],[[1, 1041],[1024, 2],[1024]],[[1, 1034],[1024, 2],[1024]],[[38],[1, 1],[1]],[[1, 53],[1, 2],[1]],[[1, 1051],[1024, 2],[1024]],[[21],[1, 1],[1]],[[1, 1047, 2048],[1024, 2],[1024, 2048]],[[1, 28],[1, 2],[1]],[[1, 1055],[1024, 2],[1024]],[[1, 1069, 2048],[1024, 2],[1024, 2048]],[[1, 46],[1, 2],[1]],[[1, 1050, 2048],[1024, 2],[1024, 2048]],[[1, 1038, 2048],[1024, 2],[1024, 2048]],[[1, 1077, 2048],[1024, 2],[1024, 2048]],[[76],[1, 1],[1]],[[1, 26],[1, 2],[1]],[[11],[1, 1],[1]],[[1, 1043, 2048],[1024, 2],[1024, 2048]],[[1, 1034, 2048],[1024, 2],[1024, 2048]],[[12],[1, 1],[1]],[[1, 1061, 2048],[1024, 2],[1024, 2048]],[[1, 1051, 2048],[1024, 2],[1024, 2048]],[[42],[1, 1],[1]],[[1, 1071],[1024, 2],[1024]],[[1, 1053],[1024, 2],[1024]],[[1, 1035],[1024, 2],[1024]],[[53],[1, 1],[1]],[[31],[1, 1],[1]],[[1, 1039, 2048],[1024, 2],[1024, 2048]],[[1, 1076],[1024, 2],[1024]],[[1, 1379],[1024, 2],[1024]],[[1, 17],[1, 2],[1]],[[1, 1059, 2048],[1024, 2],[1024, 2048]],[[1, 29],[1, 2],[1]],[[15],[1, 1],[1]],[[1, 1058],[1024, 2],[1024]],[[1, 1047],[1024, 2],[1024]],[[22],[1, 1],[1]],[[1, 1057, 2048],[1024, 2],[1024, 2048]],[[1, 1040, 2048],[1024, 2],[1024, 2048]],[[1, 39],[1, 2],[1]],[[30],[1, 1],[1]],[[1, 1049, 2048],[1024, 2],[1024, 2048]],[[1, 1059],[1024, 2],[1024]],[[1, 22],[1, 2],[1]]]
@expand_class(shapes = shape_all, dtypes=["float32", "float16"])
# shape_all = [[[1, 1056, 2048],[1024, 2],[1024, 2048]]]
# @expand_class(shapes = shape_all, dtypes=["float32"])
class TestScatterDevelopCase1_FP32(unittest.TestCase):
    def setUp(self):
        self.init_params()
        self.init_threshold()
        self.init_np_inputs_and_dout()
        self.out_torch = numpy_scatter_nd_add(self.np_x.copy(), self.np_index, self.np_updates)

    def init_params(self):
        def calc_shape(shape):
            # while len(shape) > 1 and shape[0] == 1:
            #     shape = shape[1:]
            # while len(shape) > 1 and shape[-1] == 1:
            #     shape = shape[:-1]
            return shape
        self.x_shape = calc_shape(self.shapes[0])
        self.index_shape = calc_shape(self.shapes[1])
        self.updates_shape = calc_shape(self.shapes[2])

    def init_threshold(self):
        self.atol = TOLERANCE[self.dtype]["atol"]
        self.rtol = TOLERANCE[self.dtype]["rtol"]

    def init_np_inputs_and_dout(self):
        # init np array
        self.np_x = np.random.random(size=self.x_shape).astype("float32") - 0.5
        # a = np.random.randint(0, 1 , size=1024)
        # b = np.random.randint(0, 1056 , size=1024)
        # self.np_index = np.vstack([a, b]).T
        
        self.np_index = np.vstack([np.random.randint(0, self.x_shape[i], size=self.index_shape[0:-1]) for i, _ in enumerate(range(self.index_shape[-1]))]).T

        self.np_updates = np.random.rand(*self.updates_shape).astype("float32") - 0.5
        self.np_dout = np.random.random(size=self.x_shape).astype("float32") - 0.5
        if self.dtype == "float16":
            self.np_x = self.np_x.astype("float16")
            self.np_updates = self.np_updates.astype("float16")
            self.np_dout = self.np_dout.astype("float16")

    def gen_eager_inputs_and_dout(self):
        x_eager = paddle.to_tensor(
            self.np_x,
            dtype=self.dtype if self.dtype != 'bfloat16' else "float32",
            place="gpu",
        )
        x_eager.stop_gradient = False
        index_eager = paddle.to_tensor(
            self.np_index,
            dtype="int32",
            place="gpu",
        )
        # index_eager.stop_gradient = False
        updates_eager = paddle.to_tensor(
            self.np_updates,
            dtype=self.dtype if self.dtype != 'bfloat16' else "float32",
            place="gpu",
        )
        updates_eager.stop_gradient = False
        dout_eager = paddle.to_tensor(
            self.np_dout,
            dtype=self.dtype if self.dtype != 'bfloat16' else "float32",
            place="gpu",
        )
        dout_eager.stop_gradient = False
        return x_eager, index_eager, updates_eager, dout_eager

    def cal_eager_res(self, x_eager, index_eager, updates_eager, dout_eager):
        out = paddle.scatter_nd_add(x_eager, index_eager, updates_eager)
        return out

    def test_eager_accuracy(self):
        x_eager, index_eager, updates_eager, dout_eager = self.gen_eager_inputs_and_dout()
        out_eager = self.cal_eager_res(
            x_eager, index_eager, updates_eager, dout_eager
        )

        del x_eager
        del index_eager
        del updates_eager
        del dout_eager
        paddle.device.cuda.empty_cache()
        out_eager_np = out_eager.numpy()
        del out_eager
        paddle.device.cuda.empty_cache()
        try:
        # compare develop eager forward res with torch
            np_assert_accuracy(
                out_eager_np,
                self.out_torch,
                self.atol,
                self.rtol,
                self.dtype,
                version_a="paddle_develop",
                version_b="torch",
                eager_or_static_mode="eager",
                fwd_or_bkd="forward",
                api="paddle.scatter",
            )
        except Exception as e:
            print("================================================================")
            print("scater_nd_add error: ", self.shapes[0], self.shapes[1], self.shapes[2], self.dtype)
            print(e)

if __name__ == '__main__':
    np.random.seed(2023)
    unittest.main()
