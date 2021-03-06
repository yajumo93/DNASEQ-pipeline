import os
from glob import glob
import subprocess as sp
import pandas as pd


############## hyper params ##############

seq_type = 'WES'

input_dir = r'/data/stemcell/WES/GRCh38/waiting3/35I_re/'
input_format = r'*_recal.bam'
input_bam_suffix = '_sorted_deduped_recal.bam' # 19S-72988-A10-4_sorted_deduped_recal.bam / pair info 때매 쓰는 옵션

# output_dir_name = r'mutect2_tumor_only/' # r'tumor_only/'
# output_dir_name = r'mutect2_bamout_tumor_only/'
output_dir_name = r'mutect2_stemcell/'
# output_dir_name = r'vardict_somatic_stemcell/'

# output_dir = input_dir + r'somatic_call/'
output_dir = input_dir + output_dir_name

# ref_dir = r'/data_244/refGenome/hg38/v0/'
ref_dir = r'/data/refGenome/hg38/v0/'

# ref_genome_path = ref_dir + 'Homo_sapiens_assembly38.fasta'
ref_genome_path = ref_dir + 'gdc/GRCh38.d1.vd1.fa' # gdc

# PON_path = ref_dir + r'somatic_src/mutect_PON_20151116_1000samples_over10.splited.vcf'
# PON_path = 'null'
PON_path = ref_dir + r'somatic_src/1000g_pon.hg38.vcf.gz'
# germ_src_path = ref_dir + r'somatic_src/af-only-gnomad.raw.sites.vcf.gz'
germ_src_path = ref_dir + r'somatic_src/af-only-gnomad.hg38.vcf.gz'

# sec_src_path = ref_dir + r'somatic_src/small_exac_common_3.vcf.gz'
sec_src_path = ref_dir + r'somatic_src/small_exac_common_3.hg38.vcf.gz'

# interval_path = ref_dir + r'interval_file/S07604514_Covered.bed'
interval_path = ref_dir + r'interval_file/S07604514_Padded.bed'


caller_type = 'MT2' # MT1 (Mutect1), MT2(Mutect2), SID (somatic indel detector), VAD(vardict)

# vardict 사용시 설정
VARDICT_PATH = r'/home/jun/miniconda3/envs/vardict_java/bin/'
vardict_thread = 30
vardict_af = 0.05

# tumor only mode 설정

# is_tumor_only = True
is_tumor_only = False # pair mode

# tumor only mode 사용시 설정
mutect2_tonly_inc_germline = True # tumor only 일때만 사용됨. somatic인데 germline call까지 포함할건지

# pair mode 사용시 설정
pair_info = r'/data/stemcell/WES/GRCh38/stemcell_WES_sample_pair_220318.csv'
pair_info_tumor_col_name = 'Tumor'
pair_info_normal_col_name = 'Normal'

# mutect1 사용시 설정
java7_path = r'/usr/lib/jvm/java-1.7.0/bin/java'
mutect1_path = r'/home/pbsuser/mutect1/mutect-1.1.7.jar'
gatk_legacy_path = r'/home/pbsuser/LagacyGATK/GenomeAnalysisTK.jar'

dbsnp_path = ref_dir + r'dbsnp_138.b37.vcf'
cosmic_path = ref_dir + r'cosmic_v54_120711.b37.vcf'


if os.path.isdir(output_dir) is False:
    os.mkdir(output_dir)


############### pbs config ################

pbs_N = "stem.wes_mt2"
pbs_o = output_dir + r"pbs_out_stem_vad_somatic/"
pbs_j = "oe"
pbs_l_core = 3


if os.path.isdir(pbs_o) is False:
    os.mkdir(pbs_o)

###########################################


SRC_DIR = r"/data/src/DNASEQ-pipeline/somatic_short/"

os.chdir(SRC_DIR)


pair_df = pd.read_csv(pair_info)
pair_df.set_index(pair_info_tumor_col_name, inplace=True)

pair_dict = pair_df.to_dict('index') # {tumor : {normal:_ grade:_} dict 형태. fname

# print(pair_dict)

input_lst = glob(input_dir + input_format)





for i in range(len(input_lst)):
    input_bam = input_lst[i]
    # t_name = input_bam.split(r'/')[-1].split('.')[0].split(r'_')[-1] # tumor
    t_name = input_bam.split(r'/')[-1].split('.')[0].split(r'_')[0] # tumor
    # print(t_name)

    if is_tumor_only:
        if caller_type == 'MT2':
            sp.call(f'echo "python {SRC_DIR}run_mutect2_tumor_only.py -t {t_name} -I {input_dir} \
                                                    -R {ref_genome_path} -L {interval_path} -y {seq_type} \
                                                    -P {PON_path} -S {sec_src_path} -G {germ_src_path} -O {output_dir} -g {mutect2_tonly_inc_germline}" | qsub \
                                                    -N {pbs_N} -o {pbs_o} -j {pbs_j} -l ncpus={pbs_l_core} &', shell=True)
                                                    
        elif caller_type == 'VAD':
            output_path = output_dir + 'vardict' + '_' + t_name + '.vcf'
            sp.call(f'echo "{VARDICT_PATH}vardict-java -C -G {ref_genome_path} -t -N {t_name} -b {input_bam} -c 1 -S 2 -E 3 \
                                                    -f 0.01 -th {vardict_thread} {interval_path} | {VARDICT_PATH}teststrandbias.R |\
                                                    {VARDICT_PATH}var2vcf_valid.pl -N {t_name} -Q 20 -d 30 -v 5 -f {vardict_af} > {output_path}" | qsub \
                                                    -N {pbs_N} -o {pbs_o} -j {pbs_j} -l ncpus={pbs_l_core} &', shell=True)
    else:    
        # [Tumor bam path] [Normal bam path] [Normal name] [Germline src] [Ref genome] [interval] [Output fname] [PON]

        try:
            target_normal_name = pair_dict[t_name][pair_info_normal_col_name]
            # normal_bam = input_dir + 'recal_deduped_sorted_' + target_normal_name + '.bam'
            normal_bam = input_dir + target_normal_name + input_bam_suffix
            # pair_dict[f_name]['Tumor_Grade']

            if caller_type == 'MT2':
                sp.call(f'echo "python {SRC_DIR}run_mutect2.py -n {target_normal_name} -t {t_name} -I {input_dir} -R {ref_genome_path} -L {interval_path} -y {seq_type} \
                                                -P {PON_path} -S {sec_src_path} -G {germ_src_path} -O {output_dir}" | qsub \
                                                -N {pbs_N} -o {pbs_o} -j {pbs_j} -l ncpus={pbs_l_core} &', shell=True)
            elif caller_type == 'MT1':
                out_txt_path = output_dir + t_name + '_mutect1.txt'
                out_vcf_path = output_dir + t_name + '_mutect1.vcf'
                sp.call(f'echo "sh {SRC_DIR}mutect1.sh {input_bam} {normal_bam} {ref_genome_path} {interval_path} {PON_path} \
                                                        {out_txt_path} {out_vcf_path} {dbsnp_path} {cosmic_path} {seq_type} {java7_path} {mutect1_path}" | qsub \
                                                        -N {pbs_N} -o {pbs_o} -j {pbs_j} -l ncpus={pbs_l_core} &', shell=True)

            elif caller_type == 'SID':
                out_vcf_path = output_dir + t_name + '.somaticindelocator.vcf'
                sp.call(f'echo "sh {SRC_DIR}somaticIndelDetector.sh {input_bam} {normal_bam} {ref_genome_path} {interval_path} {PON_path} \
                                                        {out_vcf_path} {dbsnp_path} {cosmic_path} {seq_type} {java7_path} {gatk_legacy_path}" | qsub \
                                                        -N {pbs_N} -o {pbs_o} -j {pbs_j} -l ncpus={pbs_l_core} &', shell=True)
            elif caller_type == 'VAD':
                output_path = output_dir + t_name + '_somatic_vardict.vcf'
                vardict_somatic_input_bam = f'"{input_bam}|{normal_bam}"'
                vardict_somatic_input_name = f'"{t_name}|{target_normal_name}"'
                
                # pair mode에서는 알수 없는 이유로 진행되지 않음. cmd만 print해서 .sh로 가져온다음 실행
                
                print(rf"{VARDICT_PATH}vardict-java -G {ref_genome_path} -t -N {t_name} -b {vardict_somatic_input_bam} -c 1 -S 2 -E 3 \
                                                    -f 0.01 -th {vardict_thread} {interval_path} | {VARDICT_PATH}testsomatic.R |\
                                                    {VARDICT_PATH}var2vcf_paired.pl -N {vardict_somatic_input_name} -Q 20 -d 30 -v 5 -f {vardict_af} > {output_path}")
                # hg38 gdc (chr1. not 1)
                # sp.call(f'echo "{VARDICT_PATH}vardict-java -G {ref_genome_path} -t -N {t_name} -b {vardict_somatic_input_bam} -c 1 -S 2 -E 3 \
                #                                     -f 0.01 -th {vardict_thread} {interval_path} | {VARDICT_PATH}testsomatic.R |\
                #                                     {VARDICT_PATH}var2vcf_paired.pl -N {vardict_somatic_input_name} -Q 20 -d 30 -v 5 -f {vardict_af} > {output_path}" | qsub \
                #                                     -N {pbs_N} -o {pbs_o} -j {pbs_j} -l ncpus={pbs_l_core} &', shell=True)
                # sp.call(f'echo "{VARDICT_PATH}vardict-java -G {ref_genome_path} -t -N {t_name} -b {vardict_somatic_input_bam} -c 1 -S 2 -E 3 \
                #                                     -f 0.01 -th {vardict_thread} {interval_path} | {VARDICT_PATH}testsomatic.R | \
                #                                     {VARDICT_PATH}var2vcf_paired.pl -Q 20 -d 30 -v 5 -f {vardict_af} > {output_path}" | qsub \
                #                                     -N {pbs_N} -o {pbs_o} -j {pbs_j} -l ncpus={pbs_l_core} &', shell=True)
                

        except KeyError as e:
            # print(f'{t_name} does not have target normal sample')
            continue
        






