def adminbounds(df, pre_df):
    output = list(set(pre_df.admin_boundary_type.unique()) - set(df.admin_boundary_type.unique()))
    print(output)
    return output