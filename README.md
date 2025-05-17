# MVGNN
This is a Pytorch code of the paper:“A multi-view graph neural network approach for magnetic resonance imaging-based diagnosis of knee injuries”

## Overview of the Framework

MVGNN is an innovative multi - view graph neural network architecture designed for knee injury diagnosis based on magnetic resonance imaging. It comprises a multi - view graph builder, a multi - view graph convolution module, and a knee injury predictor. Specifically, the multi - view graph builder utilizes the kNN algorithm to generate the adjacency matrix of the multi - view graph and employs the pretrained ResNet - 18 neural network to initialize the corresponding feature matrix. In the multi - view graph convolution module, it iteratively applies multi - layer graph neural networks to integrate local and global information of multi - view MRIs for learning informative representations. Moreover, the knee injury predictor simultaneously optimizes the view selector loss and the binary cross - entropy loss to train the model for accurate knee injury prediction. Notably, we discover that existing knee injury diagnosis methods may face the problem of insufficient feature integration and propose a comprehensive and efficient multi - view fusion mechanism to enhance the diagnostic accuracy. 

![image](https://github.com/Weilty/MVGNN/blob/main/figures/MVGNN.png)

## Training

### Requiement

This code is tested on Python 3.6 and Pytorch 1.0 + 

### Command for training:

`python train.py -name view-gcn -num_models 0 -weight_decay 0.001 -num_views 30 -cnn_name resnet18`

## The Prediction Results 

This table presents the experimental results of different methods on the ACL and Men datasets. The evaluation metrics include AUC, Accuracy, Recall, Precision, and FPS. MVGNN performs outstandingly on multiple metrics. In the ACL dataset, its AUC reaches 0.980, and the Accuracy is 0.914, etc. In the Men dataset, the Accuracy is 0.790, etc. It shows significant advantages or competitiveness compared with methods such as MRNet, Swin, MVCNN, and GVCNN. 

![image](https://github.com/Weilty/MVGNN/blob/main/figures/result.png)

The code is heavily borrowed from [mvcnn-new](https://github.com/jongchyisu/mvcnn_pytorch)