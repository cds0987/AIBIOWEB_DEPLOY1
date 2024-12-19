import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForMaskedLM
#device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device = 'cpu'
import warnings
import os


# Set logging to error only
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning)
class feedForward(nn.Module):
  def __init__(self,input_dim,hidden_dim,output_dim):
    super(feedForward, self).__init__()
    self.fc=nn.Sequential(
        nn.Linear(input_dim,hidden_dim),
        nn.ReLU(),
        nn.Linear(hidden_dim,output_dim),
        nn.Sigmoid()  
        )
    self.to(device)
  def forward(self,x):
    x=x.to(device)
    x=self.fc(x)
    return x

class CHMTR(nn.Module):
    def __init__(self):
        super(CHMTR, self).__init__()
        self.tokenizer = AutoTokenizer.from_pretrained("DeepChem/ChemBERTa-77M-MTR")
        self.base_model = AutoModelForMaskedLM.from_pretrained("DeepChem/ChemBERTa-77M-MTR")
        self.base_model.lm_head=nn.Identity()
        for param in self.base_model.parameters():
            param.requires_grad = False
        self.device = device
        self.bbbp=feedForward(384,256,1)
        self.bace=feedForward(384,256,1)
        self.ctox=feedForward(384,256,1)
        self.fda=feedForward(384,256,1)
        self.esol=feedForward(384,256,1)
        self.freesolv=feedForward(384,256,1)
        self.lipophilicity=feedForward(384,256,1)
        self.qm7=feedForward(384,256,1)

        #load weight
        self.bbbp.load_state_dict(torch.load('/content/drive/MyDrive/AI_store/Chemical_App/Source Code/AI_Model/AI_model_cache/77MTR/bbbp.pt',weights_only=False,map_location=torch.device('cpu')))
        self.bace.load_state_dict(torch.load('/content/drive/MyDrive/AI_store/Chemical_App/Source Code/AI_Model/AI_model_cache/77MTR/bace.pt',weights_only=False,map_location=torch.device('cpu')))
        self.ctox.load_state_dict(torch.load('/content/drive/MyDrive/AI_store/Chemical_App/Source Code/AI_Model/AI_model_cache/77MTR/ctox.pt',weights_only=False,map_location=torch.device('cpu')))
        self.fda.load_state_dict(torch.load('/content/drive/MyDrive/AI_store/Chemical_App/Source Code/AI_Model/AI_model_cache/77MTR/fda.pt',weights_only=False,map_location=torch.device('cpu')))
        self.esol.load_state_dict(torch.load('/content/drive/MyDrive/AI_store/Chemical_App/Source Code/AI_Model/AI_model_cache/77MTR/esol.pt',weights_only=False,map_location=torch.device('cpu')))
        self.freesolv.load_state_dict(torch.load('/content/drive/MyDrive/AI_store/Chemical_App/Source Code/AI_Model/AI_model_cache/77MTR/freesolv.pt',weights_only=False,map_location=torch.device('cpu')))
        self.lipophilicity.load_state_dict(torch.load('/content/drive/MyDrive/AI_store/Chemical_App/Source Code/AI_Model/AI_model_cache/77MTR/lipophilicity.pt',weights_only=False,map_location=torch.device('cpu')))
        self.qm7.load_state_dict(torch.load('/content/drive/MyDrive/AI_store/Chemical_App/Source Code/AI_Model/AI_model_cache/77MTR/qm7.pt',weights_only=False,map_location=torch.device('cpu')))

        self.to(device)
    def proccess_smile(self,smiles):
        return self.tokenizer(smiles, padding=True, truncation=True, return_tensors="pt").to(device)
    def forward(self, inputs,task,embedding=False):
        inputs = self.proccess_smile(inputs)
        outputs = self.base_model(**inputs, output_hidden_states=False)
        logits = outputs.logits
        ebd = logits.mean(dim=1)
        if embedding:
            return ebd
        if task=="bbbp":
            out=self.bbbp(ebd)
        elif task=="bace":
            out=self.bace(ebd)
        elif task=="ctox":
            out=self.ctox(ebd)
        elif task=="fda":
            out=self.fda(ebd)
        elif task=="esol":
            out=self.esol(ebd)
        elif task=="freesolv":
            out=self.freesolv(ebd)
        elif task=="lipophilicity":
            out=self.lipophilicity(ebd)
        elif task=="qm7":
            out=self.qm7(ebd)
        return out





    
