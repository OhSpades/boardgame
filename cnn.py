import os

from keras import regularizers
from keras.optimizers import SGD, Adam
from keras.models import load_model
from keras.models import Model as KerasModel
from keras.layers import Input, Conv2D, Flatten, Dense, BatchNormalization, LeakyReLU, Activation, add

import utils
from engine_2 import *
import copy
from config import *
from loss import softmax_cross_entropy_with_logits
player1_set, player2_set, player3_set, player4_set, player5_set, player6_set = build_sets()
player1_obj, player2_obj, player3_obj, player4_obj, player5_obj, player6_obj = build_obj_sets()
player1_inv_homes, player2_inv_homes, player3_inv_homes, player4_inv_homes, player5_inv_homes, player6_inv_homes = \
    build_invalid_homes_sets(player1_set, player2_set, player3_set, player4_set, player5_set, player6_set, player1_obj,
                             player2_obj, player3_obj, player4_obj, player5_obj, player6_obj)


class Model:
    def __init__(self, input_dim, filters, version=0):
        self.input_dim = input_dim
        self.filters = filters
        self.version = version

    def predict(self, input_board):
        logits, v = self.model.predict(np.expand_dims(input_board, axis=0).astype('float64'))
        p = utils.softmax(logits)           # Apply softmax on the logits after prediction
        return p.squeeze(), v.squeeze()     # Remove the extra batch dimension

    def save(self, save_dir, model_prefix, version):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.version = version
        self.model.save('{}/{}{:0>4}.h5'.format(save_dir, model_prefix, version))
        print('\nSaved model "{}{:0>4}.h5" to "{}"\n'.format(model_prefix, version, save_dir))

    def save_weights(self, save_dir, prefix, version):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.model.save_weights('{}/{}{:0>4}-weights.h5'.format(save_dir, prefix, version))
        utils.stress_message('Saved model weights "{}{:0>4}-weights" to "{}"'.format(prefix, version, save_dir), True)

    def load(self, filepath):
        self.model = load_model(
            filepath,
            custom_objects={'softmax_cross_entropy_with_logits': softmax_cross_entropy_with_logits}
        )
        return self.model

    def load_weights(self, filepath):
        self.model.load_weights(filepath)
        return self.model   # Return reference to model just in case



class ResidualCNN(Model):
    def __init__(self, input_dim=INPUT_DIM, filters=NUM_FILTERS):
        Model.__init__(self, input_dim, filters)
        self.model = self.build_model()


    def build_model(self):
        main_input = Input(shape=self.input_dim)
        regularizer = regularizers.l2(REG_CONST)

        x = Conv2D(filters=64, kernel_size=3, kernel_regularizer=regularizer, padding='valid')(main_input)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)
        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)
        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)

        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)
        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)
        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)

        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)
        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)
        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)

        policy = self.policy_head(x, regularizer)
        value = self.value_head(x, regularizer)

        model = KerasModel(inputs=[main_input], outputs=[policy, value])
        model.compile(loss={'policy_head':softmax_cross_entropy_with_logits, 'value_head':'mean_squared_error'}
                    , optimizer=SGD(lr=LEARNING_RATE, momentum=0.9, nesterov=True) # NOTE: keep here for reuse
                    # , optimizer=Adam(lr=LEARNING_RATE)
                    , loss_weights=LOSS_WEIGHTS)

        return model


    def value_head(self, head_input, regularizer):
        x = Conv2D(filters=1, kernel_size=1, kernel_regularizer=regularizer)(head_input)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Flatten()(x)
        x = Dense(32,
                use_bias=True,
                activation='relu',
                kernel_regularizer=regularizer)(x)
        x = Dense(1,
                use_bias=True,
                activation='tanh',
                kernel_regularizer=regularizer,
                name='value_head')(x)
        return x


    def policy_head(self, head_input, regularizer):
        x = Conv2D(filters=16, kernel_size=1, kernel_regularizer=regularizer)(head_input)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Flatten()(x)
        x = Dense(NUM_CHECKERS * BOARD_WIDTH * BOARD_WIDTH,
                use_bias=True,
                activation='linear',
                kernel_regularizer=regularizer,
                name='policy_head')(x)
        return x


    def residual_block(self, block_input, filters, kernel_size, regularizer):
        '''
        Residual block setup code referenced from Keras
        https://github.com/keras-team/keras
        '''
        x = Conv2D(filters=filters[0]
                 , kernel_size=1
                 , kernel_regularizer=regularizer)(block_input)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

        x = Conv2D(filters=filters[1]
                 , kernel_size=kernel_size
                 , padding='same'
                 , kernel_regularizer=regularizer)(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

        x = Conv2D(filters=filters[2]
                 , kernel_size=1
                 , kernel_regularizer=regularizer)(x)
        x = BatchNormalization()(x)

        x = add([x, block_input])
        x = Activation('relu')(x)
        return x


    def conv_block(self, block_input, filters, kernel_size, regularizer):
        '''
        Conv block setup code referenced from Keras
        https://github.com/keras-team/keras
        '''
        x = Conv2D(filters=filters[0]
                 , kernel_size=1
                 , kernel_regularizer=regularizer)(block_input)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

        x = Conv2D(filters=filters[1]
                 , kernel_size=kernel_size
                 , padding='same'
                 , kernel_regularizer=regularizer)(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

        x = Conv2D(filters=filters[2]
                 , kernel_size=1
                 , kernel_regularizer=regularizer)(x)
        x = BatchNormalization()(x)

        shortcut = Conv2D(filters=filters[2]
                        , kernel_size=1
                        , kernel_regularizer=regularizer)(block_input)
        shortcut = BatchNormalization()(shortcut)

        x = add([x, shortcut])
        x = Activation('relu')(x)
        return x
    # 假设已经创建了一个名为 model 的 ResidualCNN 模型对象

def get_best_move(board):
    legal_moves = board.get_legal_moves()  # 获取当前合法的移动列表
    best_move = None
    best_score = float('-inf')
    board_copy = board[:][:]

    for move in legal_moves:
        input_board = board.to_model_input()  # 将当前局面转换为模型输入
        policy, value = model.predict(input_board)  # 使用模型进行预测
        move_score = policy[move] + value  # 根据策略和价值计算移动得分

        if move_score > best_score:
            best_move = move
            best_score = move_score

    return best_move

if __name__ == '__main__':
    model = ResidualCNN()
    # test for saving
    model.model.summary()
    # plot_model(model.model, to_file='model_plot_noshowname.png', show_shapes=True, show_layer_names=False)