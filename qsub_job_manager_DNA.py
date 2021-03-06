import subprocess as sp
import glob
import natsort
import time
from time import sleep
import os

print(os.getcwd())

# script형태의 python 파일
# 사용시 hyper parameters에 해당하는 부분 유동적으로 수정
# paired end 기준으로 돌아감 

####################### hyper parameters ########################################
sample_group_name = 'stem_WES'
is_making_input_list = True

INPUT_DIR = r'/data/stemcell/WES/GRCh38/mtDNAcall_test/'   # 이 디렉토리에 계속 생성시킬것

# hg 38
# REF_GENOME_PATH = '/data_244/refGenome/hg38/v0/Homo_sapiens_assembly38.fasta'  # gatk
REF_GENOME_PATH = r'/data/refGenome/hg38/v0/gdc/GRCh38.d1.vd1.fa' # gdc
# INTERVAL_FILE_PATH = '/data_244/refGenome/hg38/v0/interval_file/S07604514_Covered.bed'
# INTERVAL_FILE_PATH = '/data_244/refGenome/hg38/v0/interval_file/S07604514_Padded.bed'
INTERVAL_FILE_PATH = r'/data/refGenome/hg38/v0/interval_file/S07604514_Padded.bed'
# INTERVAL_FILE_PATH = r'/data/refGenome/hg38/finger_target_hg38.bed'

# # b37
# REF_GENOME_PATH = '/data_244/refGenome/b37/human_g1k_v37.fasta' 
# INTERVAL_FILE_PATH = '/data_244/refGenome/b37/SureSelect_v6_processed.bed'


seq_type = "WES"
# seq_type = "WGS"

# qsub 사용 여부
is_using_qsub = True
qsub_type = "man" #  conf(옵션 컨피그 파일로 지정), man(옵션 수동지정 - openpbs)

qsub_config_name = r'/home/jun9485/src/qsub.5'

## man인 경우
pbs_N = "stemblo_WES_pp"
pbs_o = INPUT_DIR + r"pbs_stmblo_pp/"
pbs_j = "oe"
pbs_l_core = 20
SRC_DIR = r"/data/src/DNASEQ-pipeline/"



# 큐섭 사용 안하고 시퀀셜하게 진행할때
flow_sleep_time = 6000 # 초단위 
is_using_parallel = False
max_parallel_num = 2 

# Fastqc(qc) / preprocessing(pp) / germShort(gs) / somaticShort(ss) / germCNV(gc) / somaticCNV(sc)
WORKING_TYPE = "pp"

# QC
qc_output_path = 'pass'


# Data pre-processing for variant discovery    
RAW_READS = r'*.fastq.gz'
# RAW_READS = r'*.fasta'

# Germline short variant discovery (SNPs + Indels)
PROCESSED_BAM = r'*_recal.bam'
# GSDIR = r'gs/'
# GSDIR = r'GVCF/'
GSDIR = r'finger_gs/'

# VCF or GVCF 선택
HAP_MODE = 'VCF'
# HAP_MODE = 'GVCF'




if os.path.isdir(pbs_o) is False:
    os.mkdir(pbs_o)


# Somatic short variant discovery (SNVs + Indels)

# Germline copy number variant discovery (CNVs)

# Somatic copy number variant discovery (CNVs)

#################################################################################

def mk_init_file_list(_input_dir, _input_form, group_name): # fastq파일의 부재로 중간지점 스타트 불가능한 문제 해결목적
    _input_path_list = glob.glob(_input_dir + _input_form)
    _input_path_list = natsort.natsorted(_input_path_list)
    _output_path = _input_dir + sample_group_name + '.txt'
    
    f = open(f'{_output_path}', mode='w')
    for i in range(len(_input_path_list)):
        data = f'{_input_path_list[i]}\n'
        f.write(data)
    f.close


if WORKING_TYPE == 'qc':
    pass


if WORKING_TYPE == "pp":
    # Data pre-processing for variant discovery
    if is_making_input_list is True:
        mk_init_file_list(INPUT_DIR, RAW_READS, sample_group_name)
    # 한줄씩 읽어서 input_path_list에 넣기 
    f = open(rf'{INPUT_DIR}{sample_group_name}.txt', 'r')
    input_path_list = []
    for i in f.readlines():
        input_path_list.append(i[:-1])
    # input_path_list = glob.glob(INPUT_DIR + RAW_READS)    
    input_path_list = natsort.natsorted(input_path_list)
    path_len = len(input_path_list)

    print('입력할 paired end reads의 총 수 =', path_len, '\n')
    print(input_path_list)

    # exit(0) # path list 확인하고 싶으면 이거 풀기
    
    parallel_count = 0

    for i in range(path_len):
        if i%2 == 0: # 짝수면
            print(f'{input_path_list[i]} and {input_path_list[i+1]} preprocessing...')
            process = round(i/path_len, 2) * 100
            print(f'{process}% 진행')

            read1 = input_path_list[i]
            read2 = input_path_list[i+1]
            read_name = input_path_list[i].split('.')[-3].split(r'/')[-1].split(r'_')[-2] # Teratoma-13
            prefix = INPUT_DIR + read_name

            if is_using_qsub is True:
                if qsub_type == "conf":
                    sp.call(f'qsub {qsub_config_name} python preprocessing/preprocessing_DNA.py -a {read1} -b {read2} -n {read_name} -p {prefix} -i {INPUT_DIR} -R {REF_GENOME_PATH} -L {INTERVAL_FILE_PATH} -y {seq_type} &', shell=True)
                elif qsub_type == "man":
                    sp.call(f'echo "python3 {SRC_DIR}preprocessing/preprocessing_DNA.py -a {read1} -b {read2} -n {read_name} -p {prefix} -i {INPUT_DIR} -R {REF_GENOME_PATH} -L {INTERVAL_FILE_PATH} -y {seq_type}" | qsub \
                        -N {pbs_N} -o {pbs_o} -j {pbs_j} -l ncpus={pbs_l_core} &', shell=True)
            elif is_using_qsub is False:
                if max_parallel_num == 1:
                    sp.call(f'python preprocessing/preprocessing_DNA.py -a {read1} -b {read2} -n {read_name} -p {prefix} -i {INPUT_DIR} -R {REF_GENOME_PATH} -L {INTERVAL_FILE_PATH} -y {seq_type}', shell=True)
                elif max_parallel_num > 1:
                    sp.call(f'python preprocessing/preprocessing_DNA.py -a {read1} -b {read2} -n {read_name} -p {prefix} -i {INPUT_DIR} -R {REF_GENOME_PATH} -L {INTERVAL_FILE_PATH} -y {seq_type} &', shell=True)
                    parallel_count += 1
                    if parallel_count >= max_parallel_num:
                        parallel_count = 0
                        sleep(flow_sleep_time)
                else:
                    print("parallel_count must be >= 1")
                    exit(1)


elif WORKING_TYPE == "gs":
    if os.path.isdir(INPUT_DIR + GSDIR) is False:
        os.mkdir(INPUT_DIR + GSDIR)

    if os.path.isfile(INPUT_DIR + sample_group_name + '.txt') is False:
        mk_init_file_list(INPUT_DIR, PROCESSED_BAM, sample_group_name) # recal_bam list 만들기 
    
    # 한줄씩 읽어서 input_path_list에 넣기 
    f = open(rf'{INPUT_DIR}{sample_group_name}.txt', 'r')
    input_path_list = []
    for i in f.readlines():
        input_path_list.append(i[:-1])  
    input_path_list = natsort.natsorted(input_path_list)
    path_len = len(input_path_list)

    print('입력 예정 sample의 총 수 =', path_len, '\n')
    print(input_path_list)

    # exit(0) # path list 확인하고 싶으면 이거 풀기

    OUTPUT_GS_DIR = INPUT_DIR + GSDIR

    if HAP_MODE == 'VCF': # 싱글 샘플 단위 진행
        haplotype_caller_mode = 'single'
        for i in range(path_len):
            process = round(i/path_len, 2) * 100
            print(f'{process}% 진행')

            bam_file = input_path_list[i]
            # sample: recal_deduped_sorted_hiPS36-C.bam
            read_name = bam_file.split('.')[-2].split(r'/')[-1].split(r'_')[0] # hiPS36-C
            
            output_raw_vcf = OUTPUT_GS_DIR + read_name + '.vcf.gz'
            output_prefix = OUTPUT_GS_DIR + read_name

            if is_using_qsub is True:
                if qsub_type == "conf":
                    sp.call(f'qsub {qsub_config_name} python germline_short/variant_calling_single_gs.py -b {bam_file} -n {read_name} -G {OUTPUT_GS_DIR} -R {REF_GENOME_PATH} -L {INTERVAL_FILE_PATH} -y {seq_type} &', shell=True)
                elif qsub_type == "man":
                    sp.call(f'echo "python3 {SRC_DIR}germline_short/variant_calling_single_gs.py -b {bam_file} -n {read_name} -G {OUTPUT_GS_DIR} -R {REF_GENOME_PATH} -L {INTERVAL_FILE_PATH} -y {seq_type}" | qsub \
                        -N {pbs_N} -o {pbs_o} -j {pbs_j} -l ncpus={pbs_l_core} &', shell=True)
            elif is_using_qsub is False:
                if max_parallel_num == 1:
                    sp.call(f'python germline_short/variant_calling_single_gs.py -b {bam_file} -n {read_name} -G {OUTPUT_GS_DIR} -R {REF_GENOME_PATH} -L {INTERVAL_FILE_PATH} -y {seq_type}', shell=True)
                elif max_parallel_num > 1:
                    sp.call(f'python germline_short/variant_calling_single_gs.py -b {bam_file} -n {read_name} -G {OUTPUT_GS_DIR} -R {REF_GENOME_PATH} -L {INTERVAL_FILE_PATH} -y {seq_type} &', shell=True)
                    parallel_count += 1
                    if parallel_count >= max_parallel_num:
                        parallel_count = 0
                        sleep(flow_sleep_time)
                else:
                    print("parallel_count must be >= 1")
                    exit(1)
            

            # HaplotypeCaller 실행
            # sp.call(f'qsub ~/src/qsub.1 sh germline_short/make_GVCF.sh {REF_GENOME_PATH} {output_gvcf} {bam_file} {INTERVAL_FILE_PATH} {seq_type}', shell=True)
            # sp.call(f'python germline_short/variant_calling_single_gs.py -g {OUTPUT_GS_DIR} -R {REF_GENOME_PATH} -L {INTERVAL_FILE_PATH} -y {seq_type}', shell=True)

    elif HAP_MODE == 'GVCF':
        for i in range(path_len):
            process = round(i/path_len, 2) * 100
            print(f'{process}% 진행')

            bamfile = input_path_list[i]
            # sample: recal_deduped_sorted_hiPS36-C.bam
            read_name = bamfile.split('.')[-2].split(r'/')[-1].split(r'_')[0] # hiPS36-C
            
            # prefix = OUTPUT_GS_DIR + read_name
            
            output_gvcf = OUTPUT_GS_DIR + read_name + '.g.vcf.gz'
            hap_run_mode = 'gvcf'
            bamout_path = OUTPUT_GS_DIR + read_name + '_bamout.bam'
            
            # print(output_gvcf)
            # print(bamout_path)
            # exit(0)
            
            if is_using_qsub is True:
                if qsub_type == "conf":
                    pass
                elif qsub_type == "man":
                    # echo usage: $0 [RefGenome] [output.g.vcf.gz OR output.vcf.gz] [input.bam] [interval] [seqType: WGS/WES] [mode: gvcf or single] [bamout]
                    sp.call(f'echo "sh {SRC_DIR}germline_short/haplotypeCaller.sh {REF_GENOME_PATH} {output_gvcf} {bamfile} {INTERVAL_FILE_PATH} {seq_type} {hap_run_mode} {bamout_path}" | qsub \
                        -N {pbs_N} -o {pbs_o} -j {pbs_j} -l ncpus={pbs_l_core} &', shell=True)

            # HaplotypeCaller 실행
            # sp.call(f'qsub ~/src/qsub.1 sh germline_short/make_GVCF.sh {REF_GENOME_PATH} {output_gvcf} {bamfile} {INTERVAL_FILE_PATH} {seq_type}', shell=True)

        # while True:
        #     sleep(300)
        #     val = sp.check_output(f'qstat', shell=True, universal_newlines=True)
        #     if val == "":
        #         print("GVCF 생성 완료")
        #         break
        

        # sp.call(f'python germline_short/variant_calling_gs.py -g {OUTPUT_GS_DIR} -R {REF_GENOME_PATH} -L {INTERVAL_FILE_PATH} -y {seq_type}', shell=True)

    
        
    

elif WORKING_TYPE == "ss":
    pass
elif WORKING_TYPE == "gc":
    pass
elif WORKING_TYPE == "sc":
    pass


        
# case 2. germline short
