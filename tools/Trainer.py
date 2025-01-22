import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np
from tensorboardX import SummaryWriter
import math
from sklearn.metrics import precision_score, recall_score, mean_squared_error
import time
class ModelNetTrainer(object):
    def __init__(self, model, train_loader, val_loader, optimizer, loss_fn, \
                 model_name, log_dir, num_views=12):
        self.optimizer = optimizer
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.loss_fn = loss_fn
        self.model_name = model_name
        self.log_dir = log_dir
        self.num_views = num_views
        self.model.cuda()
        if self.log_dir is not None:
            self.writer = SummaryWriter(log_dir)
    def train(self, n_epochs):
        best_acc = 0
        i_acc = 0
        self.model.train()
        for epoch in range(n_epochs):
            if self.model_name == 'view_gcn':
                if epoch == 1:
                    for param_group in self.optimizer.param_groups:
                        param_group['lr'] = lr
                if epoch > 1:
                    for param_group in self.optimizer.param_groups:
                        param_group['lr'] = param_group['lr'] * 0.5 * ( 1 + math.cos(epoch * math.pi / 15))
            else:
                if epoch > 0 and (epoch + 1) % 10 == 0:
                    for param_group in self.optimizer.param_groups:
                        param_group['lr'] = param_group['lr'] * 0.5
            # permute data for mvcnn
            rand_idx = np.random.permutation(int(len(self.train_loader.dataset.filepaths) / self.num_views))
            filepaths_new = []
            for i in range(len(rand_idx)):
                filepaths_new.extend(self.train_loader.dataset.filepaths[
                                     rand_idx[i] * self.num_views:(rand_idx[i] + 1) * self.num_views])
            self.train_loader.dataset.filepaths = filepaths_new
            # plot learning rate
            lr = self.optimizer.state_dict()['param_groups'][0]['lr']
            self.writer.add_scalar('params/lr', lr, epoch)
            # train one epoch
            out_data = None
            in_data = None
            for i, data in enumerate(self.train_loader):
                if self.model_name == 'view-gcn' and epoch == 0:
                    for param_group in self.optimizer.param_groups:
                        param_group['lr'] = lr * ((i + 1) / (len(rand_idx) // 20))
                if self.model_name == 'view-gcn':
                    N, V, C, H, W = data[1].size()
                    in_data = Variable(data[1]).view(-1, C, H, W).cuda()
                else:
                    in_data = Variable(data[1].cuda())
                target = Variable(data[0]).cuda().long()
                #target_ = target.unsqueeze(1).repeat(1, 4*(10+5)).view(-1)  #20个顶点
                #target_ = target.unsqueeze(1).repeat(1, 4*(10+5)).view(-1)  #21个顶点
                target_ = target.unsqueeze(1).repeat(1, 4 * (15 + 7)).view(-1)  #30个顶点
                #target_ = target.unsqueeze(1).repeat(1, 4 * (15 + 30)).view(-1) #60个顶点
                self.optimizer.zero_grad()
                if self.model_name == 'view-gcn':
                    out_data, F_score,F_score2= self.model(in_data)
                    #print(out_data.shape)
                    #print(F_score.shape)
                    #print(F_score2.shape)
                    out_data_ = torch.cat((F_score, F_score2), 1).view(-1, 40)  #两个损失
                    #print(out_data_.shape)
                    loss = self.loss_fn(out_data, target)+ self.loss_fn(out_data_, target_) #直接相加
                else:
                    out_data = self.model(in_data)
                    loss = self.loss_fn(out_data, target)
                self.writer.add_scalar('train/train_loss', loss, i_acc + i + 1)

                pred = torch.max(out_data, 1)[1]
                results = pred == target
                correct_points = torch.sum(results.long())

                acc = correct_points.float() / results.size()[0]
                self.writer.add_scalar('train/train_overall_acc', acc, i_acc + i + 1)
                #print('lr = ', str(param_group['lr']))
                loss.backward()
                self.optimizer.step()
                log_str = 'epoch %d, step %d: train_loss %.3f; train_acc %.3f' % (epoch + 1, i + 1, loss, acc)
                if (i + 1) % 1 == 0:
                    print(log_str)
            i_acc += i
            # evaluation
            if (epoch + 1) % 1 == 0:
                with torch.no_grad():
                    loss, val_overall_acc, val_mean_class_acc, precision, recall, F1, mse, fps = self.update_validation_accuracy(epoch)
                self.writer.add_scalar('val/val_mean_class_acc', val_mean_class_acc, epoch + 1)
                self.writer.add_scalar('val/val_overall_acc', val_overall_acc, epoch + 1)
                self.writer.add_scalar('val/val_loss', loss, epoch + 1)
                self.model.save(self.log_dir, epoch)
            # save best model
                if val_overall_acc > best_acc:
                    best_acc = val_overall_acc
                print('best_acc', best_acc)
                print('precision', precision)
                print('recall', recall)
                print('F1', recall)
                print('mes', mse)
                print('fps', fps)

        # export scalar data to JSON for external processing
        self.writer.export_scalars_to_json(self.log_dir + "/all_scalars.json")
        self.writer.close()

    def update_validation_accuracy(self, epoch):
        all_correct_points = 0
        all_points = 0
        count = 0
        wrong_class = np.zeros(40)
        samples_class = np.zeros(40)
        all_loss = 0
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        start_time = time.time()  # 记录开始时间
        self.model.eval()

        for _, data in enumerate(self.val_loader, 0):

            if self.model_name == 'view-gcn':
                N, V, C, H, W = data[1].size()
                in_data = Variable(data[1]).view(-1, C, H, W).cuda()
            else:  # 'svcnn'
                in_data = Variable(data[1]).cuda()
            target = Variable(data[0]).cuda()
            if self.model_name == 'view-gcn':
                out_data,F1,F2=self.model(in_data)
            else:
                out_data = self.model(in_data)
            pred = torch.max(out_data, 1)[1]
            all_loss += self.loss_fn(out_data, target).cpu().data.numpy()
            results = pred == target

            for i in range(results.size()[0]):
                if not bool(results[i].cpu().data.numpy()):
                    wrong_class[target.cpu().data.numpy().astype('int')[i]] += 1
                    false_negatives += 1
                else:
                    true_positives += 1
                samples_class[target.cpu().data.numpy().astype('int')[i]] += 1

            false_positives += torch.sum(pred > target).cpu().data.numpy()
            correct_points = torch.sum(results.long())

            all_correct_points += correct_points
            all_points += results.size()[0]

        elapsed_time = time.time() - start_time  # 计算经过的时间
        fps = all_points / elapsed_time  # 计算每秒帧数

        precision = true_positives / (true_positives + false_positives)
        recall = true_positives / (true_positives + false_negatives)
        mse = mean_squared_error(results.cpu().data.numpy(), target.cpu().data.numpy())
        F1 = 2*precision*recall / precision+recall

        print('Total # of test models: ', all_points)
        class_acc = (samples_class - wrong_class) / samples_class
        val_mean_class_acc = np.mean(class_acc)
        acc = all_correct_points.float() / all_points
        val_overall_acc = acc.cpu().data.numpy()
        loss = all_loss / len(self.val_loader)

        print('val mean class acc. : ', val_mean_class_acc)
        print('val overall acc. : ', val_overall_acc)
        print('val loss : ', loss)
        print(class_acc)
        print('Precision: ', precision)
        print('Recall: ', recall)
        print('F1: ', F1)
        print('MSE: ', mse)
        print('FPS: ', fps)
        self.model.train()

        return loss, val_overall_acc, val_mean_class_acc, precision, recall, F1, mse, fps
