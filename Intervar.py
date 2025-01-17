#!/usr/bin/env python
#########################################################################
# Author: Lee Quan (leequan@gmail.com)
# Created Time: 2015-11-10 19:15:32 Tuesday 
# File Name: InterVar.py File type: python
# Last Change:.
# Description: python script for  Interpretation of Pathogenetic Benign
#########################################################################

import copy,logging,os,io,re,time,sys,platform,optparse

prog="InterVar"

version = """%prog 0.1
Copyright (C) 2016 Wang Genomic Lab
Lisense GPL: GNU GPL version 2 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRENTY, to the extent permittable by law.
Written by Quan LI,leequan@gmail.com. 
============================================================================
"""

usage = """Usage: %prog [OPTION] -i  INPUT -o  OUTPUT ...
       %prog  --config=config.ini ...
"""

description = """=============================================================================
InterVar                                                                       
Interpretation of Pathogenic/Benign for variants using python scripts of InterVar.
=============================================================================
"""
end = """=============================================================================
Thanks for using InterVar!
Report bugs to leequan@gmail.com;
InterVar homepage: <https://wInterVar.wglab.org>
=============================================================================
"""



if platform.python_version()< '3.0.0' :
    import ConfigParser
else:
    import configparser

paras = {}

def ConfigSectionMap(config,section):
    global paras
    options = config.options(section)
    for option in options:
        try:
            paras[option] = config.get(section, option)
            if paras[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            paras[option] = None
    return

user_evidence_dict={}

#begin read some important datsets/list firstly;
lof_genes_dict={}
aa_changes_dict={}
domain_benign_dict={}
mim2gene_dict={}
mim2gene_dict2={}
morbidmap_dict={}
morbidmap_dict2={}
PP2_genes_dict={}
BP1_genes_dict={}
PS4_snps_dict={}
exclude_snps_dict={}

def read_datasets():
#0. read the user specified evidence file
    if os.path.isfile(paras['evidence_file']):
        try:
            fh=open(paras['evidence_file'], "r")
            str = fh.read()
            for line2 in str.split('\n'):
                cls2=line2.split('\t')
                if len(cls2)>1:
                    keys=cls2[0]+"_"+cls2[1]+"_"+cls2[2]+"_"+cls2[3]
                    keys=re.sub("[Cc][Hh][Rr]","",keys)
                    user_evidence_dict[keys]=cls2[4].upper()
        except IOError:
            print("Error: can\'t read the user specified evidence file %s" % paras['evidence_file'])
        else:
            fh.close()    

#1.LOF gene list       
    try:               
        fh = open(paras['lof_genes'], "r")
        str = fh.read()
        for line2 in str.split('\n'):
            cls2=line2.split('\t')
            #print("%s %s %d" % (cls2[0], cls[Funcanno_flgs['Gene']], len(cls2[0])) )
            if len(cls2[0])>1:
                lof_genes_dict[cls2[0]]='1'
    except IOError:
        print("Error: can\'t read the LOF genes file %s" % paras['lof_genes'])
        sys.exit()
        return
    else:
        fh.close()    

#2. AA change list
    try:
        fh = open(paras['ps1_aa'], "r")
        str = fh.read()
        for line2 in str.split('\n'):
            cls2=line2.split('\t')
            if len(cls2)>1 :
                keys=cls2[0]+"_"+cls2[1]+"_"+cls2[2]+"_"+cls2[4]
                aa_changes_dict[keys]=cls2[6]
                #print("%s %s" %(keys,aa_changes_dict[keys]) )
    except IOError:
        print("Error: can\'t read the  amino acid change file %s" % paras['ps1_aa'])
        sys.exit()
    else:
        fh.close()    

#3. Domain with benign 
    try:
        fh = open(paras['pm1_domain'], "r")
        str = fh.read()
        for line2 in str.split('\n'):
            cls2=line2.split('\t')
            if len(cls2)>1:
                keys=cls2[0]+"_"+cls2[1]+": "+cls2[2]
                domain_benign_dict[keys]="1"
    except IOError:
        print("Error: can\'t read the PM1 domain  file %s" % paras['pm1_domain'])
        sys.exit()
    else:
        fh.close()   

#4. OMIM mim2gene.txt file 
    try:
        fh = open(paras['mim2gene'], "r")
        str = fh.read()
        for line2 in str.split('\n'):
            cls2=line2.split('\t')
            if len(cls2)>1:
                keys=cls2[4]
                mim2gene_dict[keys]=cls2[0]
                keys1=cls2[3]
                keys=keys1.upper()
                mim2gene_dict2[keys]=cls2[0]
    except IOError:
        print("Error: can\'t read the OMIM  file %s" % paras['mim2gene'])
        print("Error: Please download it from http://www.omim.org/downloads")
        sys.exit()
    else:
        fh.close()   

#5.PP2 gene list       
    try:               
        fh = open(paras['pp2_genes'], "r")
        str = fh.read()
        for line2 in str.split('\n'):
            cls2=line2.split('\t')
            #print("%s %s %d" % (cls2[0], cls[Funcanno_flgs['Gene']], len(cls2[0])) )
            if len(cls2[0])>1:
                PP2_genes_dict[cls2[0]]='1'
                #print("%s %d" % (cls2[0], len(cls2[0])) )
    except IOError:
        print("Error: can\'t read the PP2 genes file %s" % paras['PP2_genes'])
        sys.exit()
        return
    else:
        fh.close()    

#5.BP1 gene list       
    try:               
        fh = open(paras['bp1_genes'], "r")
        str = fh.read()
        for line2 in str.split('\n'):
            cls2=line2.split('\t')
            #print("%s %s %d" % (cls2[0], cls[Funcanno_flgs['Gene']], len(cls2[0])) )
            if len(cls2[0])>1:
                BP1_genes_dict[cls2[0]]='1'
    except IOError:
        print("Error: can\'t read the BP1 genes file %s" % paras['BP1_genes'])
        sys.exit()
        return
    else:
        fh.close()    

#6.morbidmap from OMIM  for BP5 ,  multifactorial disorders  list       
    try:               
        fh = open(paras['morbidmap'], "r")
        str = fh.read()
        for line2 in str.split('\n'):
            cls2=line2.split('|')
            #print("%s %s %d" % (cls2[0], cls[Funcanno_flgs['Gene']], len(cls2[0])) )
            #{Tuberculosis, protection against}, 607948 (3)|TIRAP, BACTS1|606252|11q24.2
            if len(cls2[0])>1 and cls2[0].find('{')==0:  # disorder start with "{"
                morbidmap_dict2[ cls2[2] ]='1'  # key as mim number 
                for cls3 in cls2[1].split(', '):
                    keys=cls3.upper()
                    morbidmap_dict[ keys ]='1'  # key as gene name
    except IOError:
        print("Error: can\'t read the OMIM morbidmap disorder file %s" % paras['morbidmap'])
        print("Error: Please download it from http://www.omim.org/downloads")
        sys.exit()
    else:
        fh.close()    

#7.prevalence of the variant with OR>5 for PS4 ,  the dataset is from gwasdb jjwanglab.org/gwasdb
    try:               
        fh = open(paras['ps4_snps'], "r")
        str = fh.read()
        for line2 in str.split('\n'):
            cls2=line2.split('\t')
            # PS4_snps_dict
            if len(cls2[0])>1:  # disorder start with "{"
                keys=cls2[0]+"_"+cls2[1]+"_"+cls2[2]+"_"+cls2[3]+"_"+cls2[4]
                PS4_snps_dict[ keys ]='1'  # key as gene name
    except IOError:
        print("Error: can\'t read the snp list file for PS4 %s" % paras['ps4_snps'])
        sys.exit()
    else:
        fh.close()    

#8. read the user specified SNP list, the variants will pass the frequency check.
    if os.path.isfile(paras['exclude_snps']):
        try:
            fh=open(paras['exclude_snps'], "r")
            str = fh.read()
            for line2 in str.split('\n'):
                cls2=line2.split('\t')
                if len(cls2)>1:
                    keys=cls2[0]+"_"+cls2[1]+"_"+cls2[2]+"_"+cls2[3]
                    keys=re.sub("[Cc][Hh][Rr]","",keys)
                    exclude_snps_dict[keys]="1"
        except IOError:
            print("Error: can\'t read the user specified SNP list file %s" % paras['exclude_snps'])
        else:
            fh.close()    


#end read datasets
    return



def check_downdb():
    path=paras['database_locat']
    path=path.strip()
    path=path.rstrip("\/")
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print("Notice: the folder of %s is created!" % path)
    else:
        print("Warning: the folder of %s is already created!" % path)
    ds=paras['database_names']
    ds.expandtabs(1);
    # database_names = refGene 1000g2014oct esp6500siv2_all avsnp144 ljb26_all clinvar_20150629 exac03 hg19_dbscsnv11 dbnsfp31a_interpro rmsk ensGene

    for dbs in ds.split():
        # os.path.isfile(options.table_annovar)
        file_name=dbs
        if dbs=="1000g2014oct":
            file_name="ALL.sites.2014_10"
        if dbs=="1000g2015aug":
            file_name="ALL.sites.2015_08"

        dataset_file=paras['database_locat']+"/"+paras['buildver']+"_"+file_name+".txt"
        if dbs != 'rmsk':
            cmd="perl "+paras['annotate_variation']+" -buildver "+paras['buildver']+" -downdb -webfrom annovar "+file_name+" "+paras['database_locat']
        if dbs == 'rmsk':
            cmd="perl "+paras['annotate_variation']+" -buildver "+paras['buildver']+" -downdb "+file_name+" "+paras['database_locat']
        if  not os.path.isfile(dataset_file):
            print("Warning: The Annovar dataset file of %s is not in %s,begin to download this %s ..." %(dbs,paras['database_locat'],dataset_file))
            print("%s" %cmd)
            os.system(cmd)

def check_input():
    inputft= paras['inputfile_type']
    if inputft.lower() == 'avinput' :
        return
    if inputft.lower() == 'vcf':
        #convert2annovar.pl -format vcf4 variantfile > variant.avinput
        cmd="perl "+paras['convert2annovar']+" -format vcf4 "+ paras['inputfile']+"> "+paras['inputfile']+".avinput"
        print("Warning: Begin to convert your vcf file of %s to AVinput of Annovar ..." % paras['inputfile'])
        print("%s" %cmd)
        os.system(cmd)
    return

def check_annovar_result():
# table_annovar.pl example/ex1.avinput humandb/ -buildver hg19 -out myanno -remove -protocol refGene,esp6500siv2_all,1000g2015aug_all,avsnp144,ljb26_all,CLINSIG,exac03   -operation  g,f,f,f,f,f,f   -nastring . -csvout
    inputft= paras['inputfile_type']
    if inputft.lower() == 'avinput' :
        cmd="perl "+paras['table_annovar']+" "+paras['inputfile']+" "+paras['database_locat']+" -buildver "+paras['buildver']+" -remove -out "+ paras['outfile']+" -protocol refGene,esp6500siv2_all,1000g2015aug_all,avsnp144,dbnsfp30a,clinvar_20160302,exac03,dbscsnv11,dbnsfp31a_interpro,rmsk,ensGene,knownGene  -operation  g,f,f,f,f,f,f,f,f,r,g,g   -nastring ."
    else:
        cmd="perl "+paras['table_annovar']+" "+paras['inputfile']+".avinput "+paras['database_locat']+" -buildver "+paras['buildver']+" -remove -out "+ paras['outfile']+" -protocol refGene,esp6500siv2_all,1000g2015aug_all,avsnp144,dbnsfp30a,clinvar_20160302,exac03,dbscsnv11,dbnsfp31a_interpro,rmsk,ensGene,knownGene   -operation  g,f,f,f,f,f,f,f,f,r,g,g   -nastring ."
    print("%s" %cmd)
    os.system(cmd)
    return

def get_gdi_rvis_lof(gene_name,line_out,dicts,temple):
    try:
        line_out=line_out+"\t"+'\t'.join(str(e) for e in dicts[gene_name])
    except KeyError:
        line_out=line_out+"\t"+'\t'.join(str(e) for e in temple)
    else:
        pass
    return(line_out)


def check_gdi_rvis_LOF(anvfile):
    gdi={}
    rvis={}
    lof={}
    newoutfile=anvfile+".grl_p"
# begin open file  and set dicts for gdi rvis and lof:
    try:
        fh = open(paras['gdi_file'], "r")
        str = fh.read()
        for line in str.split('\n'):
            cls=line.split('\t')
            if len(cls)>1:
                gdi[cls[0]]=cls[1:]
    except IOError:
        print("Error: can\'t read the annovar output file %s" % paras['gdi_file'])
        sys.exit()
        return
    else:
        pass
        fh.close()

    try:
        fh = open(paras['rvis_file'], "r")
        str = fh.read()
        for line in str.split('\n'):
            cls=line.split('\t')
            rvis['Gene']=['RVIS_ExAC_0.05%(AnyPopn)','%RVIS_ExAC_0.05%(AnyPopn)']
            if len(cls)>1:
                rvis[cls[4]]=cls[5:]
    except IOError:
        print("Error: can\'t read the annovar output file %s" % paras['rvis_file'])
        sys.exit()
        return
    else:
        pass
        fh.close()

    try:
        fh = open(paras['lof_file'], "r")
        str = fh.read()
        for line in str.split('\n'):
            cls=line.split('\t')
            if len(cls)>1:
                lof[cls[0]]=cls[1:]
    except IOError:
        print("Error: can\'t read the annovar output file %s" % paras['lof_file'])
        sys.exit()
        return
    else:
        pass
        fh.close()

    try:
        fh = open(anvfile, "r")
        fw = open(newoutfile, "w")
        str = fh.read()
        sum=0
        for line in str.split('\n'):
            cls=line.split('\t')
            if len(cls)>1:
                gene_name=cls[6]
                if cls[6] == 'Gene.refGene':
                    gene_name='Gene'
#some with multiple genes, so one gene by one gene  to annote
                gdi_temp=['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'] 
                rvis_temp=['.', '.'] 
                lof_temp=['.']
                sum=sum+1
                for gg in gene_name.split(','):
                    line_out=line+"\t"+gg
                    line_out=get_gdi_rvis_lof(gg,line_out,gdi,gdi_temp)
                    line_out=get_gdi_rvis_lof(gg,line_out,rvis,rvis_temp)
                    line_out=get_gdi_rvis_lof(gg,line_out,lof,lof_temp)
                    fw.write("%s\n" % line_out)

#        fh.write("This is my test file for exception handling!!")
    except IOError:
        print("Error: can\'t read/write the annovar output file %s %s" % (anvfile,newoutfile))
        sys.exit()
        return
    else:
        pass
        fh.close()
        fw.close()

    return(sum)

def check_genes(anvfile):
#check with multiple genes, so one gene by one gene  to annote
    newoutfile=anvfile+".grl_p"
    try:
        fh = open(anvfile, "r")
        fw = open(newoutfile, "w")
        str = fh.read()
        sum=0
        for line in str.split('\n'):
            cls=line.split('\t')
            if len(cls)>1:
                gene_name=cls[6]
                if cls[6] == 'Gene.refGene':
                    gene_name='Gene'
#some with multiple genes, so one gene by one gene  to annote
                sum=sum+1
                for gg in gene_name.split(','):
                    line_out=line+"\t"+gg
                    fw.write("%s\t\n" % line_out)

    except IOError:
        print("Error: can\'t read/write the annovar output file %s %s" % (anvfile,newoutfile))
        sys.exit()
        return
    else:
        pass
        fh.close()
        fw.close()

    return(sum)



def sum_of_list(list):
    sum=0
    for i in list:
        sum=sum+i
    return(sum)

def classfy(PVS1,PS,PM,PP,BA1,BS,BP):
    BPS=["Pathogenic","Likely pathogenic","Benign","Likely benign","Uncertain significance"]
    PAS_out=-1
    BES_out=-1
    BPS_out=4 # BPS=[4]:Uncertain significance

    PS_sum=sum_of_list(PS)
    PM_sum=sum_of_list(PM)
    PP_sum=sum_of_list(PP)
    BS_sum=sum_of_list(BS)
    BP_sum=sum_of_list(BP)
    #print("%d %d %d %d %d " %(PS_sum,PM_sum,PP_sum,BS_sum, BP_sum))
    if PS_sum ==1: 
        if PM_sum ==1 or PM_sum ==2: PAS_out=1
    if PVS1 ==1 :
        if PM_sum ==1: PAS_out=1 # 1:Likely pathogenic
    if PS_sum ==1 and PP_sum >=2: PAS_out=1
    if PM_sum >=3: PAS_out=1
    if PM_sum ==2 and PP_sum >=2: PAS_out=1
    if PM_sum ==1 and PP_sum >=4: PAS_out=1
   
    if PVS1 ==1 :
        if PS_sum >=1: PAS_out=0 # 0:Pathogenic
        if PM_sum >=2: PAS_out=0
        if PM_sum ==1 and PP_sum ==1: PAS_out=0
        if PP_sum >=2: PAS_out=0
    if PS_sum >=2: PAS_out=0
    if PS_sum ==1: 
        if PM_sum >=3: PAS_out=0
        if PM_sum ==2 and PP_sum >=2: PAS_out=0
        if PM_sum ==1 and PP_sum >=4: PAS_out=0

    if BS_sum==1 and BP_sum==1 :BES_out=3 #3:Likely benign
    if BP_sum>=2 :BES_out=3
    if BA1 ==1 or BS_sum>=2 : BES_out=2 #2:Benign

    if PAS_out != -1 and BES_out == -1: BPS_out=PAS_out
    if PAS_out == -1 and BES_out != -1: BPS_out=BES_out
    if PAS_out == -1 and BES_out == -1: BPS_out=4
    if PAS_out != -1 and BES_out != -1: BPS_out=4
    
    #print("%d %d %d " %(PAS_out,BES_out,BPS_out))

    return(BPS[BPS_out])

def check_PVS1(line,Funcanno_flgs,Allels_flgs,lof_genes_dict):
    '''
    Certain types of variants (e.g., nonsense, frameshift, canonical
    +- 1 or 2 splice sites, initiation codon, single exon or multiexon
    deletion) in a gene where LOF is a known mechanism of disease
    '''
    cls=line.split('\t')
    funcs_tmp=["nonsense","frameshift","splic","stopgain"]
    funcs_tmp2="nonframe"
    line_tmp=cls[Funcanno_flgs['Func.refGene']]+" "+cls[Funcanno_flgs['ExonicFunc.refGene']]
    PVS=0
    PVS_t1=0
    PVS_t2=0
    # Funcanno_flgs={'Func.refGene':0,'ExonicFunc.refGene':0
    for fc in funcs_tmp:
        if line_tmp.find(fc)>=0 and line_tmp.find(funcs_tmp2)<0 :
            PVS_t1=1
            break
    # wait to check LOF genes use the LoFtool_percentile,but  how to know is the disese mechanism
#    lofscore_cutoff=0.1 
#    if cls[Funcanno_flgs['LoFtool_percentile']]>0.1:
#        PVS_t2=1
    try:
        if lof_genes_dict[ cls[Funcanno_flgs['Gene']] ] == '1' :
            PVS_t2=1
    except KeyError:
        PVS_t2=0
    else:
        pass
    #print("PVSt1= %d PVSt2= %d" % (PVS_t1,PVS_t2) )
    if PVS_t1 !=0 and PVS_t2 != 0 :
        PVS=1

    return(PVS)

def check_PS1(line,Funcanno_flgs,Allels_flgs,aa_changes_dict):
    '''
    PS1 Same amino acid change as a previously established pathogenic variant regardless of nucleotide change
    Example: Val->Leu caused by either G>C or G>T in the same codon
    AAChange.refGene
    NOD2:NM_001293557:exon3:c.C2023T:p.R675W,NOD2:NM_022162:exon4:c.C2104T:p.R702W
    '''
    
    PS1=0
    PS1_t1=0
    PS1_t2=0
    cls=line.split('\t')
    funcs_tmp=["missense","nonsynony"]
    ACGTs=["A","C","G","T"]
    line_tmp=cls[Funcanno_flgs['Func.refGene']]+" "+cls[Funcanno_flgs['ExonicFunc.refGene']]

    for fc in funcs_tmp:
        if line_tmp.find(fc)>=0 :
            PS1_t1=1;
            # need to wait to check Same amino acid change as a previously pathogenic variant
            line_tmp2=cls[Funcanno_flgs['AAChange.refGene']]
            cls0=line_tmp2.split(',')
            cls0_1=cls0[0].split(':')
            aa=cls0_1[4]
            aa_last=aa[len(aa)-1:]
            #keys_tmp2=cls[Allels_flgs['Chr']]+"_"+cls[Allels_flgs['Start']]+"_"+cls[Allels_flgs['End']]+"_"+cls[Allels_flgs['Ref']]+"_"+cls[Allels_flgs['Alt']]
            keys_tmp2=cls[Allels_flgs['Chr']]+"_"+cls[Allels_flgs['Start']]+"_"+cls[Allels_flgs['End']]+"_"+cls[Allels_flgs['Alt']]
            try:
                if  aa_changes_dict[keys_tmp2]:
                    PS1_t2=0
                    #print("%s %s" %(aa_changes_dict[keys_tmp2],aa_last))
            except KeyError:
                for nt in ACGTs:
                    if nt != cls[Allels_flgs['Alt']]:
                        keys_tmp3=cls[Allels_flgs['Chr']]+"_"+cls[Allels_flgs['Start']]+"_"+cls[Allels_flgs['End']]+"_"+nt
                        try:
                            if aa_changes_dict[keys_tmp3] == aa_last:
                                PS1_t2=1
                        except KeyError:
                            pass
                        else:
                            pass

            else:
                pass


    if PS1_t1 !=0 and PS1_t2 != 0 :
        PS1=1
    return(PS1)

def check_PS2(line,Funcanno_flgs,Allels_flgs):
    '''
    De novo (both maternity and paternity confirmed) in a patient with the disease and no family history
    '''
    PS2=0
    return(PS2)


def check_PS3(line,Funcanno_flgs,Allels_flgs):
    '''
    Well-established in vitro or in vivo functional studies supportive of a damaging effect on the gene or gene
    product
    '''
    PS3=0
    '''
    cls=line.split('\t')
    line_tmp=cls[Funcanno_flgs['Gene damage prediction (all disease-causing genes)']]

    funcs_tmp=["missense","nonsynony"]
    line_tmp2=cls[Funcanno_flgs['Func.refGene']]+" "+cls[Funcanno_flgs['ExonicFunc.refGene']]
    for fc in funcs_tmp:
    
        #if line_tmp == 'Medium' or line_tmp == 'High':
        if line_tmp2.find(fc)>=0 and  (line_tmp == 'High') :
            PS3=1
    '''
    return(PS3)


def check_PS4(line,Funcanno_flgs,Allels_flgs):
    '''
    The prevalence of the variant in affected individuals is significantly increased compared with the prevalence
    in controls; OR>5 in all the gwas, the dataset is from gwasdb jjwanglab.org/gwasdb
    '''
    PS4=0
    cls=line.split('\t')
    keys_tmp2=cls[Allels_flgs['Chr']]+"_"+cls[Allels_flgs['Start']]+"_"+cls[Allels_flgs['End']]+"_"+cls[Allels_flgs['Ref']]+"_"+cls[Allels_flgs['Alt']]
    try:
        if PS4_snps_dict[keys_tmp2] == "1":
            PS4=1
    except KeyError:
        pass
    else:
        pass
    return(PS4)


def check_PM1(line,Funcanno_flgs,Allels_flgs,domain_benign_dict):
    '''
    Located in a mutational hot spot and/or critical and well-established functional domain (e.g., active site of
    an enzyme) without benign variation
    '''
    PM1=0
    PM1_t1=0
    PM1_t2=0
    cls=line.split('\t')
    funcs_tmp=["missense","nonsynony"]
    line_tmp=cls[Funcanno_flgs['Func.refGene']]+" "+cls[Funcanno_flgs['ExonicFunc.refGene']]
    for fc in funcs_tmp:
        if line_tmp.find(fc)>=0 :
            PM1_t1=1;
        # need to wait to check whether in hot spot  or  functional domain/without benign variation
    if cls[Funcanno_flgs['Interpro_domain']]!= '.' :
        keys_tmp2=cls[Allels_flgs['Chr']]+"_"+cls[Funcanno_flgs['Gene']]+": "+cls[Funcanno_flgs['Interpro_domain']]
        try:
            if domain_benign_dict[keys_tmp2] =="1":
                PM1_t2=0
                #print("PM1=0 %s" %keys_tmp2)
        except KeyError:
            PM1_t2=1
            #print("PM1=1 %s" %keys_tmp2)
        else:
            pass

    if PM1_t1==1 and PM1_t2==1 :
        PM1=1

    return(PM1)

def check_PM2(line,Freqs_flgs,Allels_flgs,Funcanno_flgs,mim2gene_dict,mim2gene_dict2):
    '''
    Absent from controls (or at extremely low frequency if recessive) (Table 6) in Exome Sequencing Project,
    1000 Genomes Project, or Exome Aggregation Consortium
    '''
    PM2=0
    #Freqs_flgs={'1000g2015aug_all':0,'esp6500siv2_all':0,'ExAC_ALL':0}
    cutoff_maf=0.005  # extremely low frequency
    cls=line.split('\t')
    mims_id="1256"

    #mim2gene_dict[keys]
    try:
        mim1=mim2gene_dict[ cls[Funcanno_flgs['Gene.ensGene']] ]
        mim2=mim2gene_dict2[cls[Funcanno_flgs['Gene']]]
        if  mims_id.find(mim1[0])!=-1 or  mims_id.find(mim2[0])!=-1:
            #print("PM2 %s %s " % (mim1,mim2))
            tt=1;
            for key in Freqs_flgs.keys():
                if(cls[Freqs_flgs[key]]!='.'):   # means absent and it is domomin
                    tt=tt*0;
            if tt==1:
                PM2=1
                #print("PM2 =1  ab and dom")
    except KeyError:  # means it is recessive
        for key in Freqs_flgs.keys():
            try:
                #if float(cls[Freqs_flgs[key]])<=cutoff_maf or float(cls[Freqs_flgs[key]])>=(1.0-cutoff_maf): 
                if float(cls[Freqs_flgs[key]])<=cutoff_maf : 
                    PM2=1
                    #print("PM2 =1  mf and res")
            except ValueError:
                PM2=0 # means absent and it is  recessive
            else:
                pass
    else:
        pass

    return(PM2)

def check_PM3(line,Funcanno_flgs,Allels_flgs):
    '''
    For recessive disorders, detected in trans with a pathogenic variant
    '''
    PM3=0
    return(PM3)

def check_PM4(line,Funcanno_flgs,Allels_flgs):
    '''
    Protein length changes as a result of in-frame deletions/insertions in a nonrepeat region or stop-loss variants
    '''
    PM4=0
    PM4_t1=0
    PM4_t2=0
    cls=line.split('\t')
    #funcs_tmp=["cds-indel","stop-loss"]
    funcs_tmp=["nonframeshift insertion","nonframeshift deletion","stoploss"]
    line_tmp=cls[Funcanno_flgs['Func.refGene']]+" "+cls[Funcanno_flgs['ExonicFunc.refGene']]
    for fc in funcs_tmp:
        if line_tmp.find(fc)>=0 :
            PM4_t1=1
        # need to wait to check  in a nonrepeat region
    if cls[Funcanno_flgs['rmsk']] == '.':
        PM4_t2=1
    if cls[Funcanno_flgs['rmsk']] != '.' and  line_tmp.find("stoploss")>=0 :
        PM4_t2=1

    if PM4_t1 !=0 and PM4_t2 != 0 :
        PM4=1

    return(PM4)

def check_PM5(line,Funcanno_flgs,Allels_flgs,aa_changes_dict):
    '''
    Novel missense change at an amino acid residue where a different missense change determined to be
    pathogenic has been seen before;Example: Arg156His is pathogenic; now you observe Arg156Cys
    NOD2:NM_001293557:exon3:c.C2023T:p.R675W,NOD2:NM_022162:exon4:c.C2104T:p.R702W
    '''
    PM5=0
    PM5_t1=0
    PM5_t2=0
    cls=line.split('\t')
    funcs_tmp=["missense","nonsynony"]
    line_tmp=cls[Funcanno_flgs['Func.refGene']]+" "+cls[Funcanno_flgs['ExonicFunc.refGene']]
    ACGTs=["A","C","G","T"]

    for fc in funcs_tmp:
        if line_tmp.find(fc)>=0 :
            PM5_t1=1;
        # need to wait to check no-Same amino acid change as a previously pathogenic variant
            line_tmp2=cls[Funcanno_flgs['AAChange.refGene']]
            cls0=line_tmp2.split(',')
            cls0_1=cls0[0].split(':')
            aa=cls0_1[4]
            aa_last=aa[len(aa)-1:]
            #keys_tmp2=cls[Allels_flgs['Chr']]+"_"+cls[Allels_flgs['Start']]+"_"+cls[Allels_flgs['End']]+"_"+cls[Allels_flgs['Ref']]+"_"+cls[Allels_flgs['Alt']]
            keys_tmp2=cls[Allels_flgs['Chr']]+"_"+cls[Allels_flgs['Start']]+"_"+cls[Allels_flgs['End']]+"_"+cls[Allels_flgs['Alt']]
            #print("%s %s %s" %(aa,aa_last,keys_tmp2))
            try:
                if  aa_changes_dict[keys_tmp2] :
                    PM5_t2=0
                    #print("PM5 %s %s" %(aa_changes_dict[keys_tmp2],aa_last))
            except KeyError:
                for nt in ACGTs:
                    if nt != cls[Allels_flgs['Alt']]:
                        keys_tmp3=cls[Allels_flgs['Chr']]+"_"+cls[Allels_flgs['Start']]+"_"+cls[Allels_flgs['End']]+"_"+nt
                        try:
                            if aa_changes_dict[keys_tmp3]:
                                PM5_t2=1
                            if aa_changes_dict[keys_tmp3] == aa_last:
                                PM5_t2=0
                        except KeyError:
                            pass
                        else:
                            pass

            else:
                pass

    if PM5_t1 !=0 and PM5_t2 != 0 :
        PM5=1
    return(PM5)

def check_PM6(line,Funcanno_flgs,Allels_flgs):
    '''
    Assumed de novo, but without confirmation of paternity and maternity
    '''
    PM6=0
    return(PM6)

def check_PP1(line,Funcanno_flgs,Allels_flgs):
    '''
    Cosegregation with disease in multiple affected family members in a gene definitively 
    known to cause the disease
    '''
    PP1=0
    return(PP1)

def check_PP2(line,Funcanno_flgs,Allels_flgs,PP2_genes_dict):
    '''
    Missense variant in a gene that has a low rate of benign missense variation and in which 
    missense variants are a common mechanism of disease
    '''
    PP2=0
    cls=line.split('\t')
    funcs_tmp=["missense","nonsynony"]
    line_tmp=cls[Funcanno_flgs['Func.refGene']]+" "+cls[Funcanno_flgs['ExonicFunc.refGene']]
    for fc in funcs_tmp:
        if line_tmp.find(fc)>=0 :
        # need to check whether gene has a low rate of benign missense variation.....
            try:
                if PP2_genes_dict[ cls[Funcanno_flgs['Gene']] ] == '1' :
                    PP2=1
            except KeyError:
                PP2=0
            else:
                pass

    return(PP2)

def check_PP3(line,Funcanno_flgs,Allels_flgs):
    '''
    Multiple lines of computational evidence support a deleterious effect on the gene or gene product
    (conservation, evolutionary, splicing impact, etc.)
    sfit for conservation, GERP++_RS for evolutionary, splicing impact from dbNSFP
    '''
    PP3=0
    PP3_t1=0
    PP3_t2=0
    PP3_t3=0
    sift_cutoff=0.05 #SIFT_score,SIFT_pred, The smaller the score the more likely the SNP has damaging effect
    PhyloP_cutoff=1.6  # phyloP46way_placental >  , The larger the score, the more conserved the site
    cutoff_conserv=2 # for GERP++_RS
    dbscSNV_cutoff=0.6    #either score(ada and rf) >0.6 as splicealtering
    
    cls=line.split('\t')
   
    try:
        if float(cls[Funcanno_flgs['SIFT_score']]) < sift_cutoff:
            PP3_t1=1
    except ValueError:  # the sift absent means many:  synonymous indel  stop, but synonymous also is no impact
        funcs_tmp=["synon","coding-synon"]
        line_tmp=cls[Funcanno_flgs['Func.refGene']]+" "+cls[Funcanno_flgs['ExonicFunc.refGene']]
        for fc in funcs_tmp:
            if line_tmp.find(fc)<0 :
                PP3_t1=1
    else:
        pass
    try:
        #if float(cls[Funcanno_flgs['phyloP46way_placental']])> PhyloP_cutoff:
        if float(cls[Funcanno_flgs['GERP++_RS']])> cutoff_conserv:
            PP3_t2=1
    except ValueError:  
        # absent means there are gaps in the multiple alignment,so cannot have the score,not conserved
        pass
    else:
        pass
    try:
        if float(cls[Funcanno_flgs['dbscSNV_RF_SCORE']])>dbscSNV_cutoff or float(cls[Funcanno_flgs['dbscSNV_ADA_SCORE']])>dbscSNV_cutoff:
            PP3_t3=1
    except ValueError:
        pass
    else:
        pass


    if (PP3_t1+PP3_t2+PP3_t3)>=3:
        PP3=1
    return(PP3)

def check_PP4(line,Funcanno_flgs,Allels_flgs):
    '''
    Patient's phenotype or family history is highly specific for a disease with a single genetic etiology
    '''
    PP4=0
    return(PP4)


def check_PP5(line,Funcanno_flgs,Allels_flgs):
    '''
    Reputable source recently reports variant as pathogenic, but the evidence is not available to the laboratory
    to perform an independent evaluation
    '''
    PP5=0
    cls=line.split('\t')

    line_tmp2=cls[Funcanno_flgs['CLINSIG']]
    if line_tmp2 != '.':
        cls3=line_tmp2.split(';')
        clinvar_bp=cls3[0]
        if clinvar_bp.find("ikely pathogenic")>=0 or clinvar_bp.find("athogenic")>=0:
            PP5=1
    return(PP5)

def check_BA1(line,Freqs_flgs,Allels_flgs):
    '''
    BA1 Allele frequency is >5% in Exome Sequencing Project, 1000 Genomes Project, or Exome Aggregation Consortium
    '''
    BA1=0
    #Freqs_flgs={'1000g2015aug_all':0,'esp6500siv2_all':0,'ExAC_ALL':0}
    cls=line.split('\t')
    for key in Freqs_flgs.keys():
        try:
            #if float(cls[Freqs_flgs[key]])>=0.05 and float(cls[Freqs_flgs[key]])<=0.5: BA1=1
            #if float(cls[Freqs_flgs[key]])>0.5 and float(cls[Freqs_flgs[key]])<=0.95: BA1=1
            if float(cls[Freqs_flgs[key]])>0.5: BA1=1

        except ValueError:
            pass
        else:
            pass

    return(BA1)

def check_BS1(line,Freqs_flgs,Allels_flgs):
    '''
    Allele frequency is greater than expected for disorder (see Table 6)
    > 1% in ESP6500all ExAc? need to check more 
    '''
    BS1=0
    cutoff=0.01 # disorder cutoff
    try:
        cutoff=float(paras['disorder_cutoff']) # user's disorder cutoff
    except ValueError:
        cutoff=0.01
    else:
        cutoff=0.01
    cls=line.split('\t')
    try:
        if cls[Freqs_flgs['ExAC_ALL']] !='.':
            #if float(cls[Freqs_flgs['ExAC_ALL']])>=cutoff and float(cls[Freqs_flgs['ExAC_ALL']])<0.5: BS1=1
            #if (1.0-float(cls[Freqs_flgs['ExAC_ALL']]))>=cutoff and float(cls[Freqs_flgs['ExAC_ALL']])>=0.5: BS1=1
            if float(cls[Freqs_flgs['ExAC_ALL']])>=cutoff : BS1=1
    except ValueError:
        pass
    else:
        pass

    return(BS1)

def check_BS2(line,Freqs_flgs,Allels_flgs):
    '''
    Observed in a healthy adult individual for a recessive (homozygous), dominant (heterozygous), or X-linked
    (hemizygous) disorder, with full penetrance expected at an early age
    check ExAC_ALL
    '''
    BS2=0
    cls=line.split('\t')
    try:
        if cls[Freqs_flgs['ExAC_ALL']] !='.':  # means the variants showed in EXAC
            # need to wait check the  disorder, with full penetrance expected at an early age?
                BS2=1
    except ValueError:
        pass
    else:
        pass


    return(BS2)

def check_BS3(line,Funcanno_flgs,Allels_flgs):
    '''
    Well-established in vitro or in vivo functional studies show no damaging effect on protein function or splicing
    '''
    BS3=0
    '''
    cls=line.split('\t')
    line_tmp=cls[Funcanno_flgs['Gene damage prediction (all disease-causing genes)']]

    funcs_tmp=["missense","nonsynony"]
    line_tmp2=cls[Funcanno_flgs['Func.refGene']]+" "+cls[Funcanno_flgs['ExonicFunc.refGene']]
    for fc in funcs_tmp:
        if line_tmp2.find(fc)>=0 and  line_tmp == 'Low' :
            BS3=1
    '''
    return(BS3)

def check_BS4(line,Funcanno_flgs,Allels_flgs):
    '''
    Lack of segregation in affected members of a family
    '''
    BS4=0
    return(BS4)

def check_BP1(line,Funcanno_flgs,Allels_flgs,BP1_genes_dict):
    '''
    Missense variant in a gene for which primarily truncating variants are known to cause disease
    truncating:  stop_gain / frameshift deletion/  nonframshift deletion
    We defined Protein truncating variants  (4) (table S1) as single-nucleotide variants (SNVs) predicted to introduce a premature stop codon or to disrupt a splice site, small insertions or deletions (indels) predicted to disrupt a transcript reading frame, and larger deletions 
    '''
    BP1=0
    cls=line.split('\t')
    funcs_tmp=["missense","nonsynony"]
    line_tmp=cls[Funcanno_flgs['Func.refGene']]+" "+cls[Funcanno_flgs['ExonicFunc.refGene']]
    for fc in funcs_tmp:
        if line_tmp.find(fc)>=0 :
        # need to wait to check whether truncating is the only cause disease
            try:
                if BP1_genes_dict[ cls[Funcanno_flgs['Gene']] ] == '1' :
                    BP1=1
            except KeyError:
                BP1=0
            else:
                pass
    return(BP1)

def check_BP2(line,Funcanno_flgs,Allels_flgs):
    '''
    Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or observed 
    in cis with a pathogenic variant in any inheritance pattern
    '''
    BP2=0
    return(BP2)

def check_BP3(line,Funcanno_flgs,Allels_flgs):
    '''
    In-frame deletions/insertions in a repetitive region without a known function
    '''
    BP3=0
    BP3_t1=0
    BP3_t2=0
    cls=line.split('\t')
    #funcs_tmp=["cds-indel","stop-loss"]
    #funcs_tmp=["nonframeshift insertion","nonframeshift insertion","nonframeshift substitution","stoploss"]
    funcs_tmp=["nonframeshift insertion","nonframeshift insertion","nonframeshift substitution"]
    line_tmp=cls[Funcanno_flgs['Func.refGene']]+" "+cls[Funcanno_flgs['ExonicFunc.refGene']]
    for fc in funcs_tmp:
        if line_tmp.find(fc)>=0 :
            BP3_t1=1;
        # need to wait to check  in a repeat region
    if cls[Funcanno_flgs['rmsk']] != '.':
        BP3_t2=1

    if BP3_t1 !=0 and BP3_t2 != 0 :
        BP3=1
    return(BP3)

def check_BP4(line,Funcanno_flgs,Allels_flgs):
    '''
    Multiple lines of computational evidence suggest no impact on gene or gene product (conservation, 
    evolutionary,splicing impact, etc.)
    '''
    BP4=0
    BP4_t1=0
    BP4_t2=0
    BP4_t3=0
    sift_cutoff=0.05 #SIFT_score,SIFT_pred, The smaller the score the more likely the SNP has damaging effect
    PhyloP_cutoff=1.6  # phyloP46way_placental >  , The larger the score, the more conserved the site
    cutoff_conserv=2 # for GERP++_RS
    dbscSNV_cutoff=0.6    #either score(ada and rf) >0.6 as splicealtering
    
    cls=line.split('\t')
    try: 
        if float(cls[Funcanno_flgs['SIFT_score']]) >= sift_cutoff:
            BP4_t1=1
    except ValueError:  # the sift absent means many:  synonymous indel  stop, but synonymous also is no impact
        funcs_tmp=["synon","coding-synon"]
        funcs_tmp2="nonsynon"
        line_tmp=cls[Funcanno_flgs['Func.refGene']]+" "+cls[Funcanno_flgs['ExonicFunc.refGene']]
        for fc in funcs_tmp:
            if line_tmp.find(fc)>=0 and line_tmp.find(funcs_tmp2)<0 :
                BP4_t1=1
    else:
        pass
    try:
        #if float(cls[Funcanno_flgs['phyloP46way_placental']]) <= PhyloP_cutoff:
        if float(cls[Funcanno_flgs['GERP++_RS']]) <= cutoff_conserv:
            BP4_t2=1
    except ValueError:
        # absent means there are gaps in the multiple alignment,so cannot have the score,not conserved
        BP4_t2=1
    else:
        pass
    try:
        if float(cls[Funcanno_flgs['dbscSNV_RF_SCORE']]) <=dbscSNV_cutoff and float(cls[Funcanno_flgs['dbscSNV_ADA_SCORE']]) <=dbscSNV_cutoff:
            BP4_t3=1
    except ValueError:
        BP4_t3=1  # means absent, this site is not in splicing consensus regions
    else:
        pass



    if (BP4_t1+BP4_t2+BP4_t3)==3:
        BP4=1
    return(BP4)


def check_BP5(line,Funcanno_flgs,Allels_flgs,morbidmap_dict):
    '''
    Variant found in a case with an alternate molecular basis for disease
    check the genes whether are for mutilfactor disorder
    '''
    BP5=0
    cls=line.split('\t')
    '''
    try:
        if morbidmap_dict[ cls[Funcanno_flgs['Gene']] ] == '1' :
            BP5=1
    except KeyError:
        BP5=0
    else:
        pass
    '''
    #diable BP5
    BP5=0
    return(BP5)

def check_BP6(line,Funcanno_flgs,Allels_flgs):
    '''
    Reputable source recently reports variant as benign, but the evidence is not available to the 
    laboratory to perform an independent evaluation; Check the ClinVar column to see whether this 
    is "benign". 
    '''
    BP6=0
    cls=line.split('\t')

    line_tmp2=cls[Funcanno_flgs['CLINSIG']]
    if line_tmp2 != '.':
        cls3=line_tmp2.split(';')
        clinvar_bp=cls3[0]
        if clinvar_bp.find("ikely benign")>=0 or clinvar_bp.find("enign")>=0:
            BP6=1

    return(BP6)

def check_BP7(line,Funcanno_flgs,Allels_flgs):
    '''
    A synonymous (silent) variant for which splicing prediction algorithms predict no impact to the 
    splice consensus sequence nor the creation of a new splice site AND the nucleotide is not highly 
    conserved
    '''
    BP7=0
    BP7_t1=0
    BP7_t2=0
    cutoff_conserv=2 # for GERP++
    cls=line.split('\t')
    funcs_tmp=["synon","coding-synon"]
    funcs_tmp2="nonsynon"
    line_tmp=cls[Funcanno_flgs['Func.refGene']]+" "+cls[Funcanno_flgs['ExonicFunc.refGene']]
    for fc in funcs_tmp:
        if line_tmp.find(fc)>=0 and line_tmp.find(funcs_tmp2)<0 :
    # need to wait to check the  impact to the splice from dbscSNV 
    # either score(ada and rf) >0.6 as splicealtering
            if cls[Funcanno_flgs['dbscSNV_RF_SCORE']]=="." or  cls[Funcanno_flgs['dbscSNV_ADA_SCORE']]==".":
                BP7_t1=1  # absent means it is not in the  splice consensus sequence
            else:
                if cls[Funcanno_flgs['dbscSNV_RF_SCORE']]<0.6 and cls[Funcanno_flgs['dbscSNV_ADA_SCORE']]<0.6:
                    BP7_t1=1
# check the conservation score of gerp++ > 2
    if cls[Funcanno_flgs['GERP++_RS']] <= cutoff_conserv or cls[Funcanno_flgs['GERP++_RS']] == '.' :
            BP7_t2=1

    if BP7_t1 !=0 and BP7_t2 != 0 :
        BP7=1        
    return(BP7)


def assign(BP,line,Freqs_flgs,Funcanno_flgs,Allels_flgs):
    PVS1=0
    PS=[0,0,0,0]
    PM=[0,0,0,0,0,0]
    PP=[0,0,0,0,0]

    BA1=0
    BS=[0,0,0,0]
    BP=[0,0,0,0,0,0,0]


    PVS1=check_PVS1(line,Funcanno_flgs,Allels_flgs,lof_genes_dict)
    
    PS1=check_PS1(line,Funcanno_flgs,Allels_flgs,aa_changes_dict)
    PS[0]=PS1
    PS2=check_PS2(line,Funcanno_flgs,Allels_flgs)
    PS[1]=PS2
    PS3=check_PS3(line,Funcanno_flgs,Allels_flgs)
    PS[2]=PS3
    PS4=check_PS4(line,Funcanno_flgs,Allels_flgs)
    PS[3]=PS4

    PM1=check_PM1(line,Funcanno_flgs,Allels_flgs,domain_benign_dict)
    PM[0]=PM1
    PM2=check_PM2(line,Freqs_flgs,Allels_flgs,Funcanno_flgs,mim2gene_dict,mim2gene_dict2)
    PM[1]=PM2
    PM3=check_PM3(line,Funcanno_flgs,Allels_flgs)
    PM[2]=PM3
    PM4=check_PM4(line,Funcanno_flgs,Allels_flgs)
    PM[3]=PM4
    PM5=check_PM5(line,Funcanno_flgs,Allels_flgs,aa_changes_dict)
    PM[4]=PM5
    PM6=check_PM6(line,Funcanno_flgs,Allels_flgs)
    PM[5]=PM6


    PP1=check_PP1(line,Funcanno_flgs,Allels_flgs)
    PP[0]=PP1
    PP2=check_PP2(line,Funcanno_flgs,Allels_flgs,PP2_genes_dict)
    PP[1]=PP2
    PP3=check_PP3(line,Funcanno_flgs,Allels_flgs)
    PP[2]=PP3
    PP4=check_PP4(line,Funcanno_flgs,Allels_flgs)
    PP[3]=PP4
    PP5=check_PP5(line,Funcanno_flgs,Allels_flgs)
    PP[4]=PP5


    BA1=check_BA1(line,Freqs_flgs,Allels_flgs)
    
    BS1=check_BS1(line,Freqs_flgs,Allels_flgs)
    BS[0]=BS1
    BS2=check_BS2(line,Freqs_flgs,Allels_flgs)
    BS[1]=BS2
    BS3=check_BS3(line,Funcanno_flgs,Allels_flgs)
    BS[2]=BS3
    BS4=check_BS4(line,Funcanno_flgs,Allels_flgs)
    BS[3]=BS4

    BP1=check_BP1(line,Funcanno_flgs,Allels_flgs,BP1_genes_dict)
    BP[0]=BP1
    BP2=check_BP2(line,Funcanno_flgs,Allels_flgs)
    BP[1]=BP2
    BP3=check_BP3(line,Funcanno_flgs,Allels_flgs)
    BP[2]=BP3
    BP4=check_BP4(line,Funcanno_flgs,Allels_flgs)
    BP[3]=BP4
    BP5=check_BP5(line,Funcanno_flgs,Allels_flgs,morbidmap_dict)
    BP[4]=BP5
    BP6=check_BP6(line,Funcanno_flgs,Allels_flgs)
    BP[5]=BP6
    BP7=check_BP7(line,Funcanno_flgs,Allels_flgs)
    BP[6]=BP7

    #print("PVS1=%s PS=%s PM=%s PP=%s BA1=%s BS=%s BP=%s" %(PVS1,PS,PM,PP,BA1,BS,BP))
     
    cls=line.split('\t')
    #begin process the exclude snp list. which will affect BA1 BS1 BS2
    if os.path.isfile(paras['exclude_snps']):
        keys=cls[Allels_flgs['Chr']]+"_"+cls[Allels_flgs['Start']]+"_"+cls[Allels_flgs['Ref']]+"_"+cls[Allels_flgs['Alt']]
        keys=re.sub("[Cc][Hh][Rr]","",keys)
        try:
            if exclude_snps_dict[keys]=="1":  
                BA1=0; 
                BS[0]=0; 
                BS[1]=0;
        except KeyError:
            pass
        else:
            pass
    #begin process the user's evidence file
    if os.path.isfile(paras['evidence_file']):
        keys=cls[Allels_flgs['Chr']]+"_"+cls[Allels_flgs['Start']]+"_"+cls[Allels_flgs['Ref']]+"_"+cls[Allels_flgs['Alt']]
        keys=re.sub("[Cc][Hh][Rr]","",keys)
        try:
            evds=user_evidence_dict[keys] #PS1=1;PM1=1;BA1=1;PVS1 PP BS BP
            for evd in evds.split(';'):
                evd_t=evd.split('=')
                if(len(evd_t)>1):
                    if int(evd_t[1])<=1:
                        #print ("%s %s %s " %(keys,evd_t[1],evd_t[0]))
                        if(evd_t[0]=="PVS1"): PVS1=evd_t[1]
                        if(evd_t[0]=="BA1"): BA1=evd_t[1]
                        if(evd_t[0].find('PS')!=-1): 
                            t=evd_t[0].find('PS'); 
                            tt=evd_t[0];
                            tt3=int(tt[t+2:t+3])
                            if(t<len(evd_t[0])-2 and tt3<=4 ): PS[tt3-1]=int(evd_t[1])
                        if(evd_t[0].find('PM')!=-1):
                            t=evd_t[0].find('PM'); 
                            tt=evd_t[0];
                            tt3=int(tt[t+2:t+3])
                            if(t<len(evd_t[0])-2 and tt3<=6 ): PM[tt3-1]=int(evd_t[1])
                        if(evd_t[0].find('PP')!=-1): 
                            t=evd_t[0].find('PP'); 
                            tt=evd_t[0];
                            tt3=int(tt[t+2:t+3])
                            if(t<len(evd_t[0])-2 and tt3<=5 ): PP[tt3-1]=int(evd_t[1])
                        if(evd_t[0].find('BS')!=-1): 
                            t=evd_t[0].find('BS'); 
                            tt=evd_t[0];
                            tt3=int(tt[t+2:t+3])
                            if(t<len(evd_t[0])-2 and tt3<=4 ): BS[tt3-1]=int(evd_t[1])
                        if(evd_t[0].find('BP')!=-1):
                            t=evd_t[0].find('BP'); 
                            tt=evd_t[0];
                            tt3=int(tt[t+2:t+3])
                            if(t<len(evd_t[0])-2 and tt3<=7 ): BP[tt3-1]=int(evd_t[1])

                    
        except KeyError:
            pass
        else:
            pass

    # end process the user's evidence file 

    cls=line.split('\t')
    if len(cls)>1:#esp6500siv2_all 1000g2015aug_all ExAC_ALL    
        BP_out=classfy(PVS1,PS,PM,PP,BA1,BS,BP)
        line_t="%s PVS1=%s PS=%s PM=%s PP=%s BA1=%s BS=%s BP=%s" %(BP_out,PVS1,PS,PM,PP,BA1,BS,BP)

        #print("%s " % BP_out)
        BP_out=line_t
        pass
    #BP=BP_out
    return(BP_out)


def search_key_index(line,dict):
    cls=line.split('\t')
    for key in dict.keys():
        for i in range(1,len(cls)):
            ii=i-1
            if key==cls[ii]:
                dict[key]=ii
                break
    return

def my_inter_var(annovar_outfile):
    newoutfile=annovar_outfile+".grl_p"
    newoutfile2=annovar_outfile+".intervar"

    Freqs_flgs={'1000g2015aug_all':0,'esp6500siv2_all':0,'ExAC_ALL':0}
    Funcanno_flgs={'Func.refGene':0,'ExonicFunc.refGene':0,'AAChange.refGene':0,'Gene':0,'Gene damage prediction (all disease-causing genes)':0,'CLNDBN':0,'CLNACC':0,'CLNDSDB':0,'dbscSNV_ADA_SCORE':0,'dbscSNV_RF_SCORE':0,'GERP++_RS':0,'LoFtool_percentile':0,'Interpro_domain':0,'rmsk':0,'SIFT_score':0,'phyloP46way_placental':0,'Gene.ensGene':0,'CLINSIG':0,'CADD_raw':0,'CADD_phred':0,'avsnp144':0,'AAChange.ensGene':0,'AAChange.knownGene':0}
    Allels_flgs={'Chr':0,'Start':0,'End':0,'Ref':0,'Alt':0}
# ExAC_ALL esp6500siv2_all   1000g2015aug_all  SIFT_score    CADD_raw    CADD_phred  GERP++_RS   phyloP46way_placental  dbscSNV_ADA_SCORE   dbscSNV_RF_SCORE   Interpro_domain

    try:
        fh=open(newoutfile, "r")
        fw=open(newoutfile2, "w")
        str=fh.read()
        line_sum=0;
        print("Notice: Begin the variants interpretation by InterVar ")
        fw.write("#%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\tclinvar: %s \t InterVar: %s \t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % ("Chr","Start","End","Ref","Alt","Ref.Gene","Func.refGene","ExonicFunc.refGene", "Gene.ensGene","avsnp144","AAChange.ensGene","AAChange.refGene","Clinvar","InterVar and Evidence","Freq_ExAC_ALL", "Freq_esp6500siv2_all","Freq_1000g2015aug_all", "CADD_raw","CADD_phred","SIFT_score","GERP++_RS","phyloP46way_placental","dbscSNV_ADA_SCORE", "dbscSNV_RF_SCORE", "Interpro_domain","AAChange.knownGene"  ))
        for line in str.split('\n'):
            BP="UNK" # the inter of pathogenetic/benign
            clinvar_bp="UNK"
            cls=line.split('\t')
            if len(cls)<2: break
            if line_sum==0:
                search_key_index(line,Freqs_flgs)
                search_key_index(line,Funcanno_flgs)
                search_key_index(line,Allels_flgs)

            else:
                #begin check the BP status from clinvar
                line_tmp2=cls[Funcanno_flgs['CLINSIG']]
                if line_tmp2 != '.':
                    cls3=line_tmp2.split(';')
                    clinvar_bp=cls3[0]
                    
                intervar_bp=assign(BP,line,Freqs_flgs,Funcanno_flgs,Allels_flgs)
                fw.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\tclinvar: %s \t InterVar: %s \t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (cls[Allels_flgs['Chr']],cls[Allels_flgs['Start']],cls[Allels_flgs['End']],cls[Allels_flgs['Ref']],cls[Allels_flgs['Alt']],cls[Funcanno_flgs['Gene']],cls[Funcanno_flgs['Func.refGene']],cls[Funcanno_flgs['ExonicFunc.refGene']], cls[Funcanno_flgs['Gene.ensGene']],cls[Funcanno_flgs['avsnp144']],cls[Funcanno_flgs['AAChange.ensGene']],cls[Funcanno_flgs['AAChange.refGene']],clinvar_bp,intervar_bp,cls[Freqs_flgs['ExAC_ALL']], cls[Freqs_flgs['esp6500siv2_all']], cls[Freqs_flgs['1000g2015aug_all']], cls[Funcanno_flgs['CADD_raw']],cls[Funcanno_flgs['CADD_phred']],cls[Funcanno_flgs['SIFT_score']],  cls[Funcanno_flgs['GERP++_RS']],cls[Funcanno_flgs['phyloP46way_placental']], cls[Funcanno_flgs['dbscSNV_ADA_SCORE']], cls[Funcanno_flgs['dbscSNV_RF_SCORE']], cls[Funcanno_flgs['Interpro_domain']],cls[Funcanno_flgs['AAChange.knownGene']]   ))
                #print("%s\t%s %s" % (line,clinvar_bp,intervar_bp))

            line_sum=line_sum+1

    except IOError:
        print("Error: can\'t readi/write the annovar output files %s" % (newoutfile,newoutfile2))
        sys.exit()
        return
    else:
        fh.close()
        fw.close()
    return(line_sum)


def main():


    if platform.python_version()< '3.0.0'  :
        config=ConfigParser.ConfigParser()
    else:
        config=configparser.ConfigParser()
    




    parser = optparse.OptionParser(usage=usage, version=version, description=description)


    parser.add_option("-?", action="help", help=optparse.SUPPRESS_HELP, dest="help")
    parser.add_option("-v", action="version", help=optparse.SUPPRESS_HELP, dest="version")
    
    parser.add_option("-c", "--config", dest="config", action="store",
                  help="The config file of all options. it is for your own configure file.You can edit all the options in the configure and if you use this options,you can ignore all the other options bellow", metavar="config.ini")

    parser.add_option("-b", "--buildver", dest="buildver", action="store",
                  help="The genomic build version, it can be hg19 and will support GRCh37 hg18 GRCh38 later", metavar="hg19")


    parser.add_option("-i", "--input", dest="input", action="store",
                  help="The input file contains your variants", metavar="example/ex1.avinput")

    parser.add_option("--input_type", dest="input_type", action="store",
                  help="The input file type, it can be  AVinput(Annovar's format),VCF", metavar="AVinput")

    parser.add_option("-o", "--output", dest="output", action="store",
                  help="The prefix of output file which contains the results, the file of results will be as [$$prefix].intervar ", metavar="example/myanno")


    group = optparse.OptionGroup(parser, "InterVar Other Options")
    group.add_option("-t", "--database_intervar", dest="database_intervar", action="store",
            help="The  database location/dir for the InterVar dataset files", metavar="intervardb")
    group.add_option("-s", "--evidence_file", dest="evidence_file", action="store",
            help="User specified Evidence file for each variant", metavar="your_evidence_file")
    parser.add_option_group(group)
    group = optparse.OptionGroup(parser, "   How to add your own Evidence for each Variant",
    """ Prepare your own evidence  file as tab-delimited,the line format:
            Chr Pos Ref_allele Alt_allele  PM1=1;BS2=1;BP3=0
                                """)
    parser.add_option_group(group)



    group = optparse.OptionGroup(parser, "Annovar Options",
                                "Caution: check these options from manual of Annovar.")
    group.add_option("--table_annovar", action="store", help="The Annovar perl script of table_annovar.pl",metavar="./table_annovar.pl",dest="table_annovar")
    group.add_option("--convert2annovar", action="store", help="The Annovar perl script of convert2annovar.pl",metavar="./convert2annovar.pl",dest="convert2annovar")
    group.add_option("--annotate_variation", action="store", help="The Annovar perl script of annotate_variation.pl",metavar="./annotate_variation.pl",dest="annotate_variation")
    group.add_option("-d", "--database_locat", dest="database_locat", action="store",
            help="The  database location/dir for the annotation datasets", metavar="humandb")

    parser.add_option_group(group)
    group = optparse.OptionGroup(parser, "Examples",
                                """./InterVar.py -c config.ini  # Run the examples in config.ini
                                 ./InterVar.py  -b hg19 -i your_input  --input_type=VCF  -o your_output 
                                """)
    parser.add_option_group(group)

    (options, args) = parser.parse_args()
    
    #(options,args) = parser.parse_args()
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit()

    print("%s" %description)
    print("%s" %version)
    print("Notice: Your command of InterVar is %s" % sys.argv[:])




    if os.path.isfile("config.ini"):
        config.read("config.ini")
        sections = config.sections()
        for section in sections:
            ConfigSectionMap(config,section)    
    else:
        print("Error: The default configure file of [ config.ini ] is not exit! Please redownload the InterVar.")
        sys.exit()

#begin to process user's options:
    if options.config != None:
        if os.path.isfile(options.config):
            config.read(options.config)
            sections = config.sections()
            for section in sections:
                ConfigSectionMap(config,section)
        else:
            print("Error: The config file [ %s ] is not here,please check the path of your config file." % options.config)
            sys.exit()

    if options.buildver != None:
        paras['buildver']=options.buildver
    if options.database_locat != None:
        paras['database_locat']=options.database_locat
    if options.input != None:
        paras['inputfile']=options.input
    if options.input_type != None:
        paras['inputfile_type']=options.input_type
    if options.output != None:
        paras['outfile']=options.output
    if options.evidence_file != None:
        paras['evidence_file']=options.evidence_file
        print("Warning: You provided your own evidence file [ %s ] for the InterVar." % options.evidence_file)
    if options.database_intervar != None:
        paras['database_intervar']=options.database_intervar

    paras['ps1_aa'] = paras['ps1_aa']+'.'+paras['buildver']
    paras['ps4_snps'] = paras['ps4_snps']+'.'+paras['buildver']
    paras['exclude_snps'] = paras['exclude_snps']+'.'+paras['buildver']

    if options.table_annovar != None:
        if os.path.isfile(options.table_annovar):
            paras['table_annovar']=options.table_annovar
        else:
            print("Error: The Annovar file [ %s ] is not here,please download ANNOVAR firstly: http://www.openbioinformatics.org/annovar" 
                    % options.table_annovar)
            sys.exit()
    if options.convert2annovar != None:
        if os.path.isfile(options.convert2annovar):
            paras['convert2annovar']=options.convert2annovar
        else:
            print("Error: The Annovar file [ %s ] is not here,please download ANNOVAR firstly: http://www.openbioinformatics.org/annovar" 
                    % options.convert2annovar)
            sys.exit()
    if options.annotate_variation != None:
        if os.path.isfile(options.annotate_variation):
            paras['annotate_variation']=options.annotate_variation
        else:
            print("Error: The Annovar file [ %s ] is not here,please download ANNOVAR firstly: http://www.openbioinformatics.org/annovar" 
                    % options.annotate_variation)
            sys.exit()


    if not os.path.isfile(paras['inputfile']):
        print("Error: Your input file [ %s ] is not here,please check the path of your input file." % paras['inputfile'])
        sys.exit()
    if  not os.path.isfile(paras['evidence_file']) and paras['evidence_file']!="None":
        print("Warning: Your specified evidence file [ %s ] is not here,please check the path of your evidence file." % paras['evidence_file'])
        print("         Your analysis will begin without your specified evidence.")


            


    print ("INFO: The options are %s " % paras)
    check_downdb()
    check_input()
    check_annovar_result() #  to obtain myanno.hg19_multianno.csv
    annovar_outfile=paras['outfile']+"."+paras['buildver']+"_multianno.txt"
    read_datasets()
    #sum1=check_gdi_rvis_LOF(annovar_outfile)
    sum1=check_genes(annovar_outfile)
    sum2=my_inter_var(annovar_outfile)

    inputfile=paras['inputfile']
    if os.path.isfile(inputfile):
        count = 0
        thefile = open(inputfile, 'rb')
        while True:
            buffer = thefile.read(8192*1024)
            if not buffer:
                break
            count += buffer.count('\n')
        thefile.close( )
        print ("Notice: About %d lines in your input file %s " % (count,inputfile))

    outfile=annovar_outfile+".intervar"
    if os.path.isfile(outfile):
        print ("Notice: About %d variants has been processed by InterVar" % (sum2-1))
        print ("Notice: The InterVar is finished, the output file is [ %s.intervar ]" % annovar_outfile)
    else:
        print ("Warning: The InterVar seems not run correctly, please check your inputs and options in configure file")

    print("%s" %end)


    

if __name__ == "__main__":
    main()


