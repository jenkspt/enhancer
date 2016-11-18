from keras.models import load_model
from PIL import Image

from loss import gradient_importance
from datagen import datagen

target_size=(224, 224)
source_rescale=(56, 56)
batch_size=6

path = '/home/ec2-user/ebs/enhancer/data/bing/test'
# path = '../../../data/test'
test_generator = datagen(path, source_rescale, target_size, batch_size, shuffle=False)

X, y = next(test_generator)

model = load_model('saved_models/model_laplace_2.h5', custom_objects={'gradient_importance': gradient_importance})

predicted = model.predict(X, batch_size=batch_size)

for i in range(batch_size):
	p_im = Image.fromarray(predicted[i].reshape(*target_size)*255).convert('RGB')
	X_im = Image.fromarray(X[i].reshape(*target_size)*255).convert('RGB')
	y_im = Image.fromarray(y[i].reshape(*target_size)*255).convert('RGB')
	p_im.save('images/p_{}.png'.format(i+1))
	X_im.save('images/X_{}.png'.format(i+1))
	y_im.save('images/y_{}.png'.format(i+1))