from tensorflow.python.summary import event_accumulator

log_path = "/home/pjs/medical-classification/view-GCN-master/view-gcn_stage_1/events.out.tfevents.1699621608.hubu-PowerEdge-R740"
ea = event_accumulator.EventAccumulator(log_path)
ea.Reload()

# ��ӡ�¼��ļ�����Ϣ
print(ea.Tags())