#!/bin/bash -e

if [ $# -lt 7 ]
then
    echo usage: $0 [INPUT_BAM_FILE] [/path/output.table] [RefGenome] [RefGenomeDir] [seqType] [interval] [refVer]
    exit 1
fi


input=$1
output=$2
ref_genome=$3
ref_dir=$4

interval=$6

refVer=$7

case "$refVer" in
    "b37")
        ks_dbSNP=$ref_dir"dbsnp_138.b37.vcf"
        ks_mills=$ref_dir"Mills_and_1000G_gold_standard.indels.b37.vcf"
        ks_1000G=$ref_dir"1000G_phase1.indels.b37.vcf"
    ;;

    "hg38")
        ks_dbSNP=$ref_dir"Homo_sapiens_assembly38.dbsnp138.vcf"
        ks_mills=$ref_dir"Mills_and_1000G_gold_standard.indels.hg38.vcf.gz"
        ks_1000G=$ref_dir"Homo_sapiens_assembly38.known_indels.vcf.gz"
    ;;

    *)
        echo "refVer = b37 or hg38"
    ;;
esac




source activate gatk4

case "$5" in
    "WES")
        gatk --java-options "-XX:ParallelGCThreads=1 -XX:ConcGCThreads=1 -Xms20G -Xmx20G" BaseRecalibrator \
            -I $input \
            -O $output \
            --known-sites $ks_dbSNP \
            --known-sites $ks_mills \
            --known-sites $ks_1000G \
            -R $ref_genome \
            --use-original-qualities \
            -L $interval
    ;;
    "WGS")
        gatk --java-options "-XX:ParallelGCThreads=1 -XX:ConcGCThreads=1 -Xms20G -Xmx20G" BaseRecalibrator \
            -I $input \
            -O $output \
            --known-sites $ks_dbSNP \
            --known-sites $ks_mills \
            --known-sites $ks_1000G \
            -R $ref_genome \
            --use-original-qualities
    ;;
    *)
        echo "seqType = WES or WGS"
        exit 1
    ;;
esac

sleep 10s
