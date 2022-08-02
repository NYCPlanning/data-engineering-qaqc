def adminbounds(df, pre_df):
    output = list(set(pre_df.admin_boundary_type.unique()) -
                  set(df.admin_boundary_type.unique()))

    if len(output) == 0:
        output = "No change"
    else:
        output = ",".join(output)

    return output
