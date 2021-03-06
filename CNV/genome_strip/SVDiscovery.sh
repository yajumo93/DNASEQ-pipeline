#!/bin/bash -e

classpath="${SV_DIR}/lib/SVToolkit.jar:${SV_DIR}/lib/gatk/GenomeAnalysisTK.jar:${SV_DIR}/lib/gatk/Queue.jar"


project_name='testPrj'
queue_name='testQ'
log_directory='/data_244/stemcell/WES/hg38_gdc/hg38_gdc_all_bam/CNV/Genome_strip/test'
workflow_manager_options='-R rusage[mem=8192]'

ref_genome='/data_244/refGenome/hg38/v0/gdc/GRCh38.d1.vd1.fa'
input_lst='/data_244/stemcell/WES/hg38_gdc/hg38_gdc_all_bam/CNV/Genome_strip/pp_inc_gendermap/stem_all_bam.list'
meta_dir='/data_244/stemcell/WES/hg38_gdc/hg38_gdc_all_bam/CNV/Genome_strip/pp_inc_gendermap/meta_data'
run_dir='/data_244/stemcell/WES/hg38_gdc/hg38_gdc_all_bam/CNV/Genome_strip/pp_inc_gendermap/run1'
run_log_dir='/data_244/stemcell/WES/hg38_gdc/hg38_gdc_all_bam/CNV/Genome_strip/pp_inc_gendermap/run1/logs'
output_path='/data_244/stemcell/WES/hg38_gdc/hg38_gdc_all_bam/CNV/Genome_strip/pp_inc_gendermap/run1/stemcell.svdiscovery.dels.vcf'
ploid_map='/data_244/FTP_DOWN/Homo_sapiens_assembly38/Homo_sapiens_assembly38.ploidymap.txt'
# interval_path='/data_244/refGenome/hg38/v0/interval_file/split_interval/whole/S07604514_Padded_onlypos_colname.bed'


java -Xmx50g -cp ${classpath} \
    org.broadinstitute.gatk.queue.QCommandLine \
    -S ${SV_DIR}/qscript/SVDiscovery.q \
    -S ${SV_DIR}/qscript/SVQScript.q \
    -cp ${classpath} \
    -gatk ${SV_DIR}/lib/gatk/GenomeAnalysisTK.jar \
    -configFile ${SV_DIR}/conf/genstrip_parameters.txt \
    -R ${ref_genome} \
    -I ${input_lst} \
    -md ${meta_dir} \
    -runDirectory ${run_dir} \
    -jobLogDir ${run_log_dir} \
    -O ${output_path} \
    -minimumSize 100 \
    -maximumSize 100000 \
    -ploidyMapFile ${ploid_map} \
    -run