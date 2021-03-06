
"""
sample들의pyclone input을 rbind 해주는 코드

사용 안함 !!!

"""

from ntpath import join
import pandas as pd
import os
from glob import glob


input_dir = r'E:/UTUC_data/gdc_hg38/maf/3rd/DP_AF_filtered_maf/True_maf/True_positive_maf/pyclone_inputs'
# input_dir = r'E:/UTUC_data/gdc_hg38/maf/2nd/DP_AF_filtered_maf/True_maf/True_positive_maf/pyclone_inputs'
# input_dir = r'E:/UTUC_data/gdc_hg38/maf/pyclone_input'
input_format = '*.tsv'

# output_name = 'UTUC_2nd_pyclone_mergedInput.tsv'
output_name = 'UTUC_2nd_3rd_pyclone_mergedInput.tsv'

save_path = os.path.join(input_dir, output_name)

input_path_lst = glob(os.path.join(input_dir, input_format))

print(input_path_lst)

res_df = pd.DataFrame(columns=['mutation_id', 'ref_counts', 'var_counts', \
                                'normal_cn', 'minor_cn', 'major_cn'])


# row_count = 0

for input_data in input_path_lst:

    input_df = pd.read_csv(input_data, sep='\t')
    # print(input_df)

    # row_count = row_count + input_df.shape[0]

    res_df = pd.concat([res_df, input_df])
    # break


# print(row_count)
print(res_df.shape)




res_df.to_csv(save_path, index=False, sep='\t')