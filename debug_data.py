
import pandas as pd
import os

try:
    df = pd.read_csv("./data/social_stream.csv")
    print(f"Total Rows: {len(df)}")
    
    # Check Columns
    print(f"Columns: {df.columns.tolist()}")
    
    # Check is_launch
    print("\nValue Counts for is_launch:")
    print(df['is_launch'].value_counts())
    
    # Normalize
    df['is_launch'] = df['is_launch'].astype(str).replace({'True': True, 'False': False, 'true': True, 'false': False})
    df['post_id'] = df['post_id'].astype(str).str.strip()
    df['parent_id'] = df['parent_id'].fillna("").astype(str).str.strip().replace("nan", "")
    
    parents = df[df['is_launch'] == True]
    children = df[df['is_launch'] == False]
    
    print(f"\nParents: {len(parents)}")
    print(f"Children: {len(children)}")
    
    # Check Matches
    matches = 0
    for idx, child in children.iterrows():
        pid = child['parent_id']
        if pid in parents['post_id'].values:
            matches += 1
        else:
            print(f"Orphan Child! Parent ID: '{pid}'")
            
    print(f"\nMatched Children: {matches}")
    
    if len(children) > 0:
        print("\nSample Child:")
        print(children.iloc[0])

except Exception as e:
    print(f"Error: {e}")
