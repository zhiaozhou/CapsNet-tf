import tensorflow as tf
import numpy as np
from pdb import set_trace

def _int64_feature(value):
  return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def _bytes_feature(value):
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def make_tf_example(image_string, classes):
    return tf.train.Example(
        features=tf.train.Features(
            feature={
                'image': tf.train.Feature(
                    bytes_list=tf.train.BytesList(value=[image_string])),
                'label': tf.train.Feature(
                    int64_list=tf.train.Int64List(value=classes)),
            }
        )
    )


def pad_to44(img, shape=[44, 44, 1]):
    '''shape=[h, w]'''
    result = np.zeros([44, 44, 1])
    result[8:36, 8:36, :] = img
    return result


def random_crop(img, shape=36):
    i, j = np.random.choice(range(9), 2)
    return img[i: i + shape, j: j + shape, :]



h, w, c = 36, 36, 1

N_OUTPUT = 60000000
K = 10  # num of classes
N = 1000  # num of proliferation per image 

# a simple TF graph here
np_img = tf.placeholder(tf.uint8, shape=[h, w, c])
png_img = tf.image.encode_png(np_img)


def pad_crop_merge_save(base_pack, additional_pack, tfpack):
    xi, i = base_pack
    xo, o = additional_pack
    xo = random_crop(pad_to44(xo))
    combined_img = np.concatenate([xi, xo], -1)
    combined_img = np.max(combined_img, -1, keepdims=True)

    png_encoded = tfpack['sess'].run(
        tfpack['png_img'], feed_dict={tfpack['np_img']: combined_img})

    ex = make_tf_example(png_encoded, [i, j])
    tfpack['writer'].write(ex.SerializeToString())


def main():
    (x, y), (x_t, y_t) = tf.keras.datasets.mnist.load_data()

    if len(x.shape) == 3:
        x = np.expand_dims(x, -1)
        x_t = np.expand_dims(x_t, -1)

    x = [x[y==i] for i in range(10)]
    x_t = [x_t[y_t==i] for i in range(10)]

    sess = tf.Session()
    tfr_writer = tf.python_io.TFRecordWriter('MultiMNIST.tfr')

    n_per_class, remainder = divmod(N, K - 1)
    count = 1
    for i in range(10):
        x_digit_i = x[i]
        other_class = set(range(10)) - set([i])
        for xi in x_digit_i:
            xi = random_crop(pad_to44(xi)) 
            for j in other_class:
                Nj = x[j].shape[0]

                index = np.random.choice(range(Nj), n_per_class, replace=False)
                imgs_from_that_class = x[j][index]
                
                for xo in imgs_from_that_class:
                    # pad_crop_merge_save(
                    #     base_pack=(xi, i),
                    #     additional_pack=(xo, o),
                    #     tfpack={'sess': sess, np_p}
                    # )

                    xo = random_crop(pad_to44(xo))
                    combined_img = np.concatenate([xi, xo], -1)
                    combined_img = np.max(combined_img, -1, keepdims=True)

                    png_encoded = sess.run(png_img, feed_dict={np_img: combined_img})

                    ex = make_tf_example(png_encoded, [i, j])
                    tfr_writer.write(ex.SerializeToString())

                    print('\rProcessing {:08d}/{:08d}...'.format(c, N_OUTPUT), end='')
                    c += 1


            for _ in range(remainder):
                j = np.random.choice(list(other_class))
                Nj = x[j].shape[0]
                index = np.random.choice(range(Nj))
                xo = x[j][index]

                xo = random_crop(pad_to44(xo))
                combined_img = np.concatenate([xi, xo], -1)
                combined_img = np.max(combined_img, -1, keepdims=True)
                png_encoded = sess.run(png_img, feed_dict={np_img: combined_img})

                ex = make_tf_example(png_encoded, [i, j])
                tfr_writer.write(ex.SerializeToString())

                print('\rProcessing {:08d}/{:08d}...'.format(c, N_OUTPUT), end='')
                c += 1
                    # with open('./dataset/MultiMNIST/img{}{}-{:08d}.png'.format(i, j, c), 'wb') as fp:
                    #     fp.write(png_encoded)
    print()
    tfr_writer.close()
    sess.close()

# encoded_png = tf.image.encode_png(x[0][0])


# tf.train.Example
#     tf.train.Features


# def _int64_feature(value):
#   return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


# def _bytes_feature(value):
#   return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))






# # =====================
# import tensorflow as tf
# import numpy as np

# img = np.random.normal(size=[28, 28, 1])
# label0, label1 = 0, 1

# # encoded_png = tf.image.encode_png(img)
# example = tf.train.Example(
#     features=tf.train.Features(
#         feature={
#             'label0': _int64_feature(label0),
#             'label1': _int64_feature(label1),
#             # 'shape': _bytes_feature(shape),
#             'image': _bytes_feature(img.tostring())
#         }
#     )
# )

# # feature_lists=tf.train.FeatureLists(
# #     feature_list={
# #         'label': tf.train.Feature(
# #             int64_list=tf.train.Int64List(value=[0, 1])
# #         )
# #     }
# # )

# # tf.train.FeatureList()

# writer.write(example.SerializeToString())
# with tf.python_io.TFRecordWriter('./test') as writer:
#     writer.write()

