
Reversing Image Redaction with Deep Learning
============================================

### [Penn Jenks](https://www.linkedin.com/in/pennjenks)

* [Inspiration](#the-inspiration)  
* [Data](#the-data)  
* [Model](#the-model)  
* [Results](#the-results)
* [Analysis](#analysis)
* [Sources](#sources)
* [Code](https://github.com/jenkspt/enhancer/tree/master/src/models/enhancer)

![Grid of redacted faces](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/slides/redacted_grid.jpg "Redacted Images")

## The Inspiration
#### [*AI Can Recognize Your Face Even If You’re Pixelated*][WIRED]
I was inspired to create this project after reading the above Wired Magazine article 
(which covered this [reasearch paper][REDACTION PAPER]).  

Here are the relevent exerpts:

> "Researchers at the University of Texas at Austin and Cornell Tech say that they’ve trained a piece 
> of software that can undermine the privacy benefits of standard content-masking techniques like 
> blurring and pixelation by learning to read or see what’s meant to be hidden in images—anything 
> from a blurred house number to a pixelated human face in the background of a photo.""

> "To execute the attacks, the team trained neural networks to perform image recognition by feeding 
> them data from four large and well-known image sets for analysis.""

> "Once the neural networks achieved roughly 90 percent accuracy or better on identifying relevant 
> objects in the training sets, the researchers obfuscated the images using the three privacy tools 
> and then further trained their neural networks to interpret blurred and pixelated images based on 
> knowledge of the originals"

*Here is the part that I found especially interesting:*  

> "... the research isn’t doing image reconstruction from scratch, and can’t reverse 
> the obfuscation to actually recreate pictures of the faces or objects it’s identifying.

### *I took this as a challenge!*
##### The goal of this project is to take an obviscated image of a face and reconstruct the orignal.

Still wondering what image redaction is?  
![Image redaction example](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/slides/face_pixelate_example.jpg "Identity Redaction")

## The Data
#### 300,000 Faces
I used the bing image API to download 300,000 images of faces exactly 224x224 pixels. As it turns out, The Bing
image search API can do everything that the Google one can do, but its 1000 times cheaper, and they gave me $200.

* Bing API Code: [bing_faces.py](https://raw.githubusercontent.com/jenkspt/enhancer/master/src/utilities/bing_faces.py)
* Image URLs: [bing.zip](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/bing.zip)
* Image Download Script: [download_bing_images.py](https://raw.githubusercontent.com/jenkspt/enhancer/master/src/utilities/download_bing_images.py)

I used about 10000 of these for the validation set.

## The Model
#### Self-supervised Deep Learning Regression
As it turns out, reconstructing a 224x224 resolution image is really difficult. While the classification problem 
(identifying people) has probably several hundred to perhaps several thousands of classes, the regression problem 
has 50,176 target features. In order to simplify this problem converted all of the images to grayscale.

> "As it turns out, reconstructing a 224x224 resolution image is really difficult"

This is a self-supervised learning model rather than just a supervised learning model because of the way the model is trained. 
Instead of having a bunch of input features and corresponding labels, the 'self-supervised' part means
I am doing some kind of transform on the target, and using the result as the input. Also it only makes sense to use
deep learning when the transform is lossy, or else the model would just be learning the inverse of the transform.

I simulated image redaction by scaling the input image down to 1/16th of its original size, effectively throwing out 94% of the data. 
I then used a standard resampling method to scale the image back up to its original size. This is the self-supervised part, which effectively 
throws out 94% or the original data ([This is actually debatable](#analysis))  
> "I simulated image redaction by scaling the input image down to 1/16th of its original size, effectively throwing out 94% of the data."  

![Input Scaling](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/slides/input_scale.jpg "Self-Supervised Input")
The architechture is similar to that of an autoencoder. If you are familiar with deep learning, you should jump right to the 
[code](https://github.com/jenkspt/enhancer/tree/master/src/models/enhancer/model.py). Its written using [Keras][KERAS] 
(on top of [TensorFlow][TENSORFLOW]), so its super easy to understand. If you are not familiar with deep learning, you can think 
of it as a way of doing image compression.

*Most deep learning reasearch papers show some kind of representation of the architecture, so I drew some boxes ...*  
![Model Architecture](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/slides/architecture.jpg "Model Architecture")

I decided to train this model on a dataset of faces, because I was hoping that it could internaly learn the representation
of a face, and therefore be better at hallucinating the reconstruction of more detailed features such as the eyes, ears and nose.

![Prediction with Amy Schumer](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/slides/prediction_shumer.jpg "Amy Schumer")

## The Results
#### Did I Mention I Love Cosmos?  
Keep in mind that the model has not seen any of these test images.  

![Prediction with Neil deGrasse Tyson](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/slides/prediction_tyson.jpg "Neil deGrasse Tyson")
![Prediction with President Barack Obama](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/slides/prediction_obama_large.jpg "Neil deGrasse Tyson")
![predictions Gates Burgundy Clinton](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/slides/predictions_gates_burgundy_clinton.jpg "Gates Burgundy Clinton Sandwich")
![predictions Bazos Jobs Jenks](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/slides/predictions_bazos_jobs_jenks.jpg "Bazos Jobs Jenks Sandwich")
*Thats me at the bottom ... can't remember who those other guys are.*

## Analysis
I ended up using **mean absolute error** for the loss function. I tried using mean squared error, but the pixel values would revert
toward the mean, resulting in a gray, washed-out image. I also tried a more sophisticated manipulation of the loss function by weighting 
pixel errors by their Laplace gradient. I eventually realized that the Laplace gradient is much the same as the convolutional operation in
my network, and so I'm not sure where I was going with that one ...

![predictions Obama](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/slides/prediction_obama_1.jpg "President Barack Obama")

The average error of the validation images, after the 15th epoch, was around 2.5%. The Obama prediction has an error rate of 2.4% 
error, which means, on average each pixel is off by an intensity of 6 in the range from 0-255. This sounds pretty good, but unfortunately, this
doesn't tell the whole story. As a result of using the MAE for the loss, the majority of the pixels have much, much smaller error, while a 
smaller percentage have a much higher error.

By taking the difference of the prediction and the original image, we can represent the error, where white is no error, and full red saturation
is 100% error.

![predictions Obama](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/slides/prediction_obama_4.jpg "President Barack Obama")

By taking the difference of the input image and the original, we discover that the baseline error rate is about 4.6%. This means we achieved
4.6% error just by scaling up the image.

By taking the difference of the baseline and the prediction error, we can represent the a more accurate representation of the information that 
is actually being recovered by the deep learning model.

![predictions Obama](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/slides/prediction_obama_5.jpg "President Barack Obama")
![predictions Obama](https://raw.githubusercontent.com/jenkspt/enhancer/master/data/slides/prediction_obama_6.jpg "President Barack Obama")

## Future Work
#### When Google Does What You Want To Do ... But Better
*Almost...*
There are many many ways I can improve on this project, but it is a good proof of concept that this kind of work
is even possible. If you have made it this far, I suggest you read the following reasearch for yourself.

* [*Colorful Image Colorization*][COLORIZER PAPER]
* [Image Compression with Neural Networks](GOOGLE JPEG BLOG)
	* [Full Resolution Image Compression with Recurrent Neural Networks](GOOGLE JPEG PAPER)


## Sources
* [*AI Can Recognize Your Face Even If You’re Pixelated*][WIRED]  
	* [*Defeating Image Obfuscation with Deep Learning*][REDACTION PAPER]
* [*Colorful Image Colorization*][COLORIZER PAPER]
* [Image Compression with Neural Networks](GOOGLE JPEG BLOG)
	* [Full Resolution Image Compression with Recurrent Neural Networks](GOOGLE JPEG PAPER)

[WIRED]: https://www.wired.com/2016/09/machine-learning-can-identify-pixelated-faces-researchers-show
[REDACTION PAPER]: https://www.cs.cornell.edu/~shmat/shmat_imgobfuscation.pdf
[COLORIZER PAPER]: https://arxiv.org/pdf/1603.08511.pdf
[GOOGLE JPEG BLOG]: https://research.googleblog.com/2016/09/image-compression-with-neural-networks.html
[GOOGLE JPEG PAPER]: https://arxiv.org/pdf/1608.05148v1.pdf
[KERAS]: https://keras.io/
[TENSORFLOW]: https://www.tensorflow.org/