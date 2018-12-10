import re
import pandas as pd

from .elastic import do_query


def query_to_column_name(query, query_type):
    return "_".join(query.split()+[query_type])


def process_query_result(result):
    results = []
    for hit in result['hits']['hits']:
        doc_id = hit['_id']
        tf_string = hit['_explanation']['details'][0]['description']
        tf = int(re.search(r'termFreq=(\d+)\.', tf_string)[1])
        results.append((doc_id, tf))
    return results


def add_members_columns(speeches_df, members_path, columns):
    members_df = pd.read_csv(members_path, usecols=['member_id']+columns)
    new_df = speeches_df.merge(
        members_df, left_on='speaker_id',
        right_on='member_id', how='left').drop('member_id', axis=1
    )
    return new_df 


def add_results_to_dataframe(parsed_results, dataframe, column_name):
    id_col = "speech_id"
    extra_col_df = pd.DataFrame.from_records(
        parsed_results,
        columns=[id_col, column_name]
    )
    new_df = dataframe.merge(extra_col_df, on=id_col, how="left")
    # replace missing values from query results with zeroes, and then convert
    # back to integerss as the missing values from the merge caused casting to
    # floats
    return new_df.fillna(0).astype({column_name:int})


def make_dataset(dataset_df, query, index_name, size, query_type):
    results = do_query(query, index_name, size, query_type)
    parsed_results = process_query_result(results)
    column_name = query_to_column_name(query, query_type)
    return add_results_to_dataframe(parsed_results, dataset_df, column_name)

