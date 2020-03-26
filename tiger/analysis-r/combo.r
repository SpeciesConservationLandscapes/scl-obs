pbso.integrated=function(){
	beta.names=colnames(X.back)
	beta.names[1]='beta0'
	alpha.names=colnames(W.back)
	alpha.names[1]='alpha0'
	psign.names=paste("p_sign_",c(1:Npsign),sep="")
	pcam.names=paste("p_cam_",c(1:NpCT),sep="")
	par.names=c(beta.names,	alpha.names, psign.names,pcam.names)
	paramGuess = rep(0,length(par.names))
	fit.pbso = optim(par=paramGuess, fn=negLL.int,method='BFGS', hessian=TRUE) 
	se.pbso<-rep(NA,length(fit.pbso$par))
	if (fit.pbso$convergence==0) se.pbso = sqrt(diag(solve(fit.pbso$hessian)))
	tmp=data.frame(par.names,fit.pbso$par,se.pbso)
	names(tmp)=c('Parameter name', 'Value', 'Standard error')
	p=NULL
	p$coefs=tmp
	p$convergence=fit.pbso$convergence
	p$optim_message=fit.pbso$message
	p$value=fit.pbso$value
	return(p)
	}
negLL.int<-function(par){
	beta <- par[1:Nx]
	alpha <- par[(Nx+1):(Nx+Nw)]
	p_sign<-plogis(par[(Nx+Nw+1):(Nx+Nw+Npsign)])
	p_cam<-plogis(par[(Nx+Nw+Npsign+1):(Nx+Nw+Npsign+NpCT)])
	lambda = exp(as.matrix(X.back) %*% beta)
    psi =1- exp(-lambda)
	tw=as.matrix(W.back) %*% alpha
	p_thin = plogis(tw)
	zeta<-matrix(NA,ncol=2,nrow=length(psi))
	zeta[,1]<-1-psi
	zeta[,2]<-log(psi)
		for (i in 1:length(CT$det)){
		zeta[CT$cell[i],2]<-zeta[CT$cell[i],2]+CT$det[i]*log(p_cam[CT$PI[i]])+(CT$days[i]-CT$det[i])*log(1-p_cam[CT$PI[i]])
		}
	for (i in 1:length(sign$dets)){
		zeta[sign$cell[i],2]<-zeta[sign$cell[i],2]+sign$dets[i]*log(p_sign[sign$survey.id[i]])+(sign$reps[i]-sign$dets[i])*log(1-p_sign[sign$survey.id[i]])
		}
	known_occ<-unique(c(sign$cell[sign$dets>0],CT$cell[CT$det>0]))
	zeta[known_occ,1]<-0
	lik.so<-ifelse(zeta[,1]==0,zeta[,2],log(zeta[,1])+zeta[,2])
	nll.po = -1*(-1*sum(lambda*p_thin)+sum(log(lambda[po_data]*p_thin[po_data])))
	nll.so = -1*sum(lik.so)
	nll.so+nll.po
	}
####### read in data
setwd("C:/Users/cyackulic/Documents/GitHub/scl-obs")
wcovars<-c("tri","distance_to_roads") # covariates that might bias presence-only data
xcovars<-c("woody_cover","hii") # covariates that might affect tiger presence
griddata <- read.csv("tiger/data/200130_Sumatragrid_covariates.csv")[,c("gridcode",wcovars,xcovars)]
griddata<-subset(griddata,is.na(rowSums(griddata[,-1]))==FALSE)
means<-apply(griddata[,-1],2,mean)
sds<-apply(griddata[,-1],2,sd)
griddata[,-1]<-(griddata[,-1]-rep(means,each=dim(griddata)[1]))/rep(sds,each=dim(griddata)[1])
X.back<-cbind(1,griddata[,xcovars])
colnames(X.back)<-c("Int",xcovars)
W.back<-cbind(1,griddata[,wcovars])
colnames(W.back)<-c("Int",wcovars)
#
po_data<-unique(read.csv("tiger/data/prob 2/Ad Hoc v9 Sumatra 25NOV2019_V2_singleheader_srtm_hii.csv")$cell.label)
po_data<-subset(match(paste(po_data),griddata[,1]),is.na(match(po_data,griddata[,1]))==FALSE) #remove any po_data that is in a grid cell not listed in griddata
#
tsign <- read.csv("tiger/data/Tiger_observation_entry_9_SS_Observations_SUMATRA.csv")
tsign$survey.id<-as.numeric(tsign[,1])
tsign$uni<-paste(tsign$survey.id,tsign$grid.cell.label)
sign<-data.frame(uni=unique(tsign$uni),survey.id=NA,cell=NA,reps=NA,dets=NA)
for (i in 1:length(sign$uni)){
	t<-subset(tsign,tsign$uni==sign$uni[i])
	sign$survey.id[i]<-t$survey.id[1]
	sign$cell[i]<-match(t$grid.cell.label[1],griddata$gridcode)
	sign$reps[i]<-t$X..replicates.surveyed[1]
	sign$dets[i]<-ifelse(dim(t)[1]==1,t$observation,dim(t)[1])
	}
sign<-subset(sign,is.na(sign$cell)==FALSE)
# would be better to link lon-lat to grid cells and calculate days camera traps at large before bringing this into r
#couldn't find Leuser observation data so only using BBSNP
CTobs <- read.csv("tiger/data/Tiger_observation_entry_9_CT_observations_BBSNP_V2.csv",stringsAsFactors=F)[,1:8]
CTdep <- read.csv("tiger/data/Tiger_observation_entry_9_CT_deployments_latlon_BBSNP.csv",stringsAsFactors=F)[,c("project.ID","deployment.ID","camera.longitude","camera.latitude","deployment.date.time","pickup.date.time")]
CTdep<-subset(CTdep,CTdep[,6]!="NONE")
CTll<-read.csv("tiger/data/camera_latlon_gridcode.csv") # I created this file by saving dbf as a csv
pasted<-function(x){paste(x[1],x[2])}
CTdep$cell<-CTll$gridcode[match(apply(CTdep[,4:3],1,pasted),apply(CTll[,3:4],1,pasted))]
CTdep$deploy<-julian(as.Date(CTdep[,6]))-julian(as.Date(CTdep[,5]))
CTdep$det<-NA
for (i in 1:length(CTdep$det)){
	temp<-subset(CTobs,CTobs$project.ID==CTdep$project.ID[i]&CTobs$deployment.ID==CTdep$deployment.ID[i]&rowSums(CTobs[,4:8],na.rm=TRUE)>0)
	CTdep$det[i]<-length(unique(julian(as.Date(temp$observation.date.time,, "%m/%d/%y")))) # should format to have same format as other dates
	}
CT<-data.frame(PI=as.numeric(as.factor(CTdep$project.ID)),cell=match(CTdep$cell,griddata$gridcode),days=CTdep$deploy,det=CTdep$det)
CT<-subset(CT,is.na(CT$cell)==FALSE)
Nx<-1+length(xcovars)
Nw<-1+length(wcovars)
Npsign<-max(sign$survey.id)
NpCT<-max(CT$PI) 
m<-pbso.integrated()
