import os
import pandas as pd
import numpy as np
from pathlib import Path


def comb_names(eventsdf, fst_colname: str = "trial_type", scnd_colname: 
    str = None, new_colname: str = "new_trialtype"):
    """
    Prepare events dataframe by creating a new column that combines values from two columns,
    with the second column converted to lowercase.
    
    Args:
        eventsdf: DataFrame containing event data
        fst_colname: Name of the first column to use in combination (default: "trial_type")
        scnd_colname: Name of the second column to use in combination (required)
        new_colname: Name of the new column to create (default: "new_trialtype")
        
    Returns:
        DataFrame with the newly added combined column
    """
    if scnd_colname is None:
        raise ValueError("scnd_colname parameter is required")

    # Check specified columns exist in the DataFrame
    if fst_colname not in eventsdf.columns:
        raise ValueError(f"Column '{fst_colname}' not found in DataFrame")
    
    if scnd_colname not in eventsdf.columns:
        raise ValueError(f"Column '{scnd_colname}' not found in DataFrame")
        
    eventsdf[new_colname] = eventsdf[fst_colname] + '_' + eventsdf[scnd_colname].str.lower()
    return eventsdf


def add_reactiontime_regressor(eventsdf, trial_type_col='trial_type', resp_trialtype: str = 'response', response_colname: str = 'response_time', 
                                rtreg_name: str ='rt_reg', onset_colname: str = 'onset', duration_colname: str = 'duration', new_trialtype:str = None):
    """
    Pull reaction time regressor rows and add them to the dataframe as regressor
    Assumes reaction times are in miliseconds, converts [times] / 10000, to convert to seconds for "duration"
    
    Parameters
    ----------
    eventsdf : DataFrame containing event data w/ response times
    trial_type_col (str): Column name for identifying response trials, default='trial_type'
    resp_trialtype (str): Condition in trial_type_col that has associated response times, default 'response'
    response_colname (str) : Column name containing response time in milliseconds, default='response_time'
    rtreg_name (str) : Name for new reaction time regressor, default='rt'
    onset_colname (str) : Name for onset times column, default = 'onset'
    duration_colname (str) : Name for duration times column, default = 'duration'
    new_trialtype (str): Whether to save the response type under new trial, default = None

    Returns
    -------
    DataFrame with reaction time regressor rows added
    """
    # Create reaction time regressor rows
    if new_trialtype:
        new_trial_name = new_trialtype
    else:
        new_trial_name = trial_type_col

    if isinstance(resp_trialtype, str):
        resp_trialtype = [resp_trialtype]


    rt_reg_rows = eventsdf[eventsdf[trial_type_col].isin(resp_trialtype)].copy()
    rt_reg_rows[new_trial_name] = rtreg_name
    rt_reg_rows[duration_colname] = rt_reg_rows[response_colname] / 1000  # Convert ms to seconds
    rt_reg_rows = rt_reg_rows[[onset_colname, duration_colname, new_trial_name]]
    
    # Concatenate with original dataframe
    return pd.concat([eventsdf, rt_reg_rows], ignore_index=True)


def prep_gamble_events(eventsdf: pd.DataFrame, trialtype_colname: str = 'trial_type',
                       incl_trialtypes: list = None, modtype: str = "hcp", 
                       new_trialcol_name: str = 'new_trialtype'):
    """
    Prepare gambling task events dataframe by cleaning and transforming trial data.
    
    Handles missing data, creates new trial type designations and 
    processes different modality types (HCP vs non-HCP). 
    
    Parameters
    ----------
    eventsdf: DataFrame containing event data with columns for onset times and trial types
    trialtype_colname (str): Column name containing the trial type information, default='trial_type'
    incl_trialtypes (list): List of trial types to include; if None, all types are included (optional)
    modtype (str): either "hcp" or another value for different processing, default="hcp"
    new_trialcol_name (str):  Name for the new column containing processed trial types, default='new_trialtype'
        
    Returns
    -------
    pd.DataFrame: Processed copy of the events dataframe with added/modified columns
    """
    # Handle missing onsets
    missing_count = eventsdf['onset'].isna().sum()
    if missing_count > 0:
        print(f"Dropping {missing_count} rows with None/NaN in 'onsets' column.")
        eventsdf = eventsdf.dropna(subset=['onset'])
    else:
        print("No None/NaN values found in 'onsets' column.")
    
    # Create a copy to avoid modifying the original
    eventdf_cpy = eventsdf.copy()
    
    if modtype == "hcp":
        if len(incl_trialtypes) < 1:
            raise ValueError(f"No values are subset from {incl_trialtypes}, required for Gambling task")
        else:
            # Filter by trial types and process
            eventdf_cpy = eventdf_cpy[eventdf_cpy[trialtype_colname].isin(incl_trialtypes)].copy()
            eventdf_cpy[new_trialcol_name] = (eventdf_cpy[trialtype_colname] + '_' + 
                                             eventdf_cpy['mostly_reward'].map({1: 'reward', 0: 'loss'}))
            return eventdf_cpy
    else:
        # Non-HCP processing
        eventdf_cpy[new_trialcol_name] = eventdf_cpy[trialtype_colname]
        
        # Process quest_mark trials
        quest_mask = eventdf_cpy[trialtype_colname] == 'quest_mark'
        eventdf_cpy.loc[quest_mask, new_trialcol_name] = (
            eventdf_cpy.loc[quest_mask, trialtype_colname].str.split('_').str[0] + '_' + 
            eventdf_cpy.loc[quest_mask, 'response'].apply(
                lambda x: 'lwr' if x == 2 else 'hihr' if x == 3 else 'othr')
        )
        
        # Process feedback trials
        feedback_mask = eventdf_cpy[trialtype_colname] == "feedback"
        eventdf_cpy.loc[feedback_mask, 'feedback_type'] = (
            eventdf_cpy.loc[feedback_mask, 'feedback_type']
            .fillna(0)
            .astype(int)
            .astype(str)
        )
        eventdf_cpy.loc[feedback_mask, new_trialcol_name] = "feedback_" + eventdf_cpy.loc[feedback_mask, 'reward_type'].str.lower()
        
        # Filter by trial types if specified
        if len(incl_trialtypes) > 0:
            return eventdf_cpy[eventdf_cpy[trialtype_colname].isin(incl_trialtypes)].copy()

        return eventdf_cpy


def prep_motor_events(eventsdf: pd.DataFrame, trialtype_colname: str = 'trial_type',
                      incl_trialtypes: list = None,  modtype: str = "hcp"):
    """
    Prepare motor task events dataframe by processing and filtering trial types.
    
    
    Parameters
    ----------
    eventsdf : pd.DataFrame
    trialtype_colname (str) : Column name where conditions/trials are labeled, default='trial_type'
    incl_trialtypes (list, optional): List of trial types to include; if None, all types are included (optional)
    modtype (str): Modality type, controls processing logic; currently only "hcp" has special handling, default="hcp"
        
    Returns
    -------
    pd.DataFrame: Processed copy of the events dataframe with trial types consolidated as needed
    """
    eventdf_cpy = eventsdf.copy()

    if modtype == "hcp":
        # Combine "cue_*" types into single regressor
        cue_mask = eventdf_cpy['trial_type'].str.contains('cue', na=False)
        eventdf_cpy.loc[cue_mask, trialtype_colname] = eventdf_cpy.loc[cue_mask, trialtype_colname].str.split('_').str[0]

    # filter by list when specified
    if len(incl_trialtypes) > 0:
        return eventdf_cpy[eventdf_cpy[trialtype_colname].isin(incl_trialtypes)].copy()
    
    return eventdf_cpy



def prep_social_events(eventsdf: pd.DataFrame,  trialtype_colname: str = 'trial_type',
                       incl_trialtypes: list = None, modtype: str = "hcp", new_trialcol_name: str = 'new_trialtype'):
    """
    Prepare social task events dataframe by combining trial type with social context information.
    
    This function processes social task events, combines column information to create new trial
    designations, and handles additional processing for alternative modality types.
    
    Parameters
    ----------
    eventsdf : DataFrame containing event data with columns for trial types and social context
    trialtype_colname (str): Column name containing the trial type information, default='trial_type'
    incl_trialtypes (list): List of trial types to include; if None, all types are included, optional
    modtype (str):  Modality type, either "hcp" or "alt" for alternative processing
    new_trialcol_name (str): Name for the new column containing processed trial types default='new_trialtype'
         
    Returns
    -------
    Processed copy of the events dataframe with combined trial type information
    """
    if modtype not in ['hcp', 'alt']:
        raise ValueError(f"Incorrect model provided: {modtype}. Should be 'hcp' or 'alt'")
    
    eventdf_cpy = eventsdf.copy()
    # filter by trial types
    if len(incl_trialtypes) > 0:
        eventdf_cpy = eventdf_cpy[eventdf_cpy[trialtype_colname].isin(incl_trialtypes)].copy()
    
    # Combine names to create new trial type col
    eventdf_cpy = comb_names(eventsdf=eventdf_cpy, fst_colname=trialtype_colname, scnd_colname='social_type', new_colname=new_trialcol_name)
    
    # processing for alt model
    if modtype == 'alt':
        # reaction time regressor rows
        eventdf_cpy = add_reactiontime_regressor(eventdf_cpy, trial_type_col='trial_type', resp_trialtype='response', 
        response_colname='response_time', rtreg_name='rt', new_trialtype=new_trialcol_name)

    return eventdf_cpy


def prep_language_events(eventsdf: pd.DataFrame,  trialtype_colname: str = 'trial_type',
                       incl_trialtypes: list = None, modtype: str = "hcp", new_trialcol_name: str = 'new_trialtype'):
    """
    Prepare language task events dataframe by combining trial type with social context information.
    
    This function processes social task events, combines column information to create new trial
    designations, and handles additional processing for alternative modality types.
    
    Parameters
    ----------
    eventsdf : DataFrame containing event data with columns for trial types and social context
    trialtype_colname (str): Column name containing the trial type information, default='trial_type'
    incl_trialtypes (list): List of trial types to include; if None, all types are included, optional
    modtype (str):  Modality type, either "hcp" or "alt" for alternative processing
    new_trialcol_name (str): Name for the new column containing processed trial types default='new_trialtype'
         
    Returns
    -------
    Processed copy of the events dataframe with combined trial type information
    """
    if modtype not in ['hcp', 'alt']:
        raise ValueError(f"Incorrect model provided: {modtype}. Should be 'hcp' or 'alt'")
    
    eventdf_cpy = eventsdf.copy()
    # filter by trial types
    if len(incl_trialtypes) > 0:
        eventdf_cpy = eventdf_cpy[eventdf_cpy[trialtype_colname].isin(incl_trialtypes)].copy()
    

    # processing for alt model
    if modtype == 'alt':
        # reaction time regressor rows
        eventdf_cpy = add_reactiontime_regressor(eventsdf=eventdf_cpy, trial_type_col='trial_type', resp_trialtype=['story_answerfull', 
        'math_answerfull','dmath_answerfull'], 
        response_colname='response_time', rtreg_name='rt')

    return eventdf_cpy

def prep_relation_events(eventsdf: pd.DataFrame,  trialtype_colname: str = 'trial_type',
                       incl_trialtypes: list = None, modtype: str = "hcp", new_trialcol_name: str = 'new_trialtype'):
    """
    Prepare relational task events dataframe by combining trial type with social context information.
    
    This function processes social task events, combines column information to create new trial
    designations, and handles additional processing for alternative modality types.
    
    Parameters
    ----------
    eventsdf : DataFrame containing event data with columns for trial types and social context
    trialtype_colname (str): Column name containing the trial type information, default='trial_type'
    incl_trialtypes (list): List of trial types to include; if None, all types are included, optional
    modtype (str):  Modality type, either "hcp" or "alt" for alternative processing
    new_trialcol_name (str): Name for the new column containing processed trial types default='new_trialtype'
         
    Returns
    -------
    Processed copy of the events dataframe with combined trial type information
    """
    if modtype not in ['hcp', 'alt']:
        raise ValueError(f"Incorrect model provided: {modtype}. Should be 'hcp' or 'alt'")
    
    
    
    # filter by trial types
    if modtype == 'hcp':
        if len(incl_trialtypes) > 0:
            eventdf_cpy = eventsdf[eventsdf[trialtype_colname].isin(incl_trialtypes)].copy()
    

    elif modtype == 'alt':
        if len(incl_trialtypes) > 0:
            # reaction time regressor rows
            eventsdf_rt = add_reactiontime_regressor(eventsdf=eventsdf, trial_type_col=trialtype_colname, resp_trialtype=['relation_stim', 'control_stim'], 
            response_colname='response_time', rtreg_name='rt')

            eventdf_cpy = eventsdf_rt[eventsdf_rt[trialtype_colname].isin(incl_trialtypes)].copy()

    return eventdf_cpy


def prep_emotion_events(eventsdf: pd.DataFrame,  trialtype_colname: str = 'trial_type',
                       incl_trialtypes: list = None, modtype: str = "hcp", new_trialcol_name: str = 'new_trialtype'):
    """
    Prepare emotion task events dataframe by combining trial type with social context information.
    
    This function processes social task events, combines column information to create new trial
    designations, and handles additional processing for alternative modality types.
    
    Parameters
    ----------
    eventsdf : DataFrame containing event data with columns for trial types and social context
    trialtype_colname (str): Column name containing the trial type information, default='trial_type'
    incl_trialtypes (list): List of trial types to include; if None, all types are included, optional
    modtype (str):  Modality type, either "hcp" or "alt" for alternative processing
    new_trialcol_name (str): Name for the new column containing processed trial types default='new_trialtype'
         
    Returns
    -------
    Processed copy of the events dataframe with combined trial type information
    """
    if modtype not in ['hcp', 'alt']:
        raise ValueError(f"Incorrect model provided: {modtype}. Should be 'hcp' or 'alt'")
    
    
    
    # filter by trial types
    if modtype == 'hcp':
        if len(incl_trialtypes) > 0:

            eventdf_cpy = eventsdf.copy() 
            # specify the blocks to start from cue
            for block_type in eventdf_cpy['block_type'].unique():
                # For each block type (Shape_Block1, Face_Block1, etc.)
                block_rows = eventdf_cpy[eventdf_cpy['block_type'] == block_type]
                
                cue_row = block_rows[block_rows['trial_type'].str.startswith('cue_')].iloc[0]
                block_row = block_rows[block_rows['trial_type'].str.endswith('_block')].iloc[0]
                
                # Get the indices
                block_idx = block_row.name
                
                # Set the block onset to match the cue onset
                eventdf_cpy.at[block_idx, 'onset'] = cue_row['onset']
                
                # Set the block duration to sum of cue and block durations
                eventdf_cpy.at[block_idx, 'duration'] = cue_row['duration'] + block_row['duration']

            eventdf_cpy = eventdf_cpy[eventdf_cpy[trialtype_colname].isin(incl_trialtypes)].copy()

    elif modtype == 'alt':
        if len(incl_trialtypes) > 0:
            eventdf_cpy = eventsdf[eventsdf[trialtype_colname].isin(incl_trialtypes)].copy()

    return eventdf_cpy

import pandas as pd

def prep_wm_events(eventsdf: pd.DataFrame, trialtype_colname: str = "trial_type",incl_trialtypes: list = None, 
    modtype: str = "hcp", new_trialcol_name: str = "new_trialtype"):
    """
    Prepare working memory task events dataframe by combining trial type with social context information.
    
    Parameters:
    eventsdf: DataFrame containing event data with columns for trial types and social context.
    trialtype_colname (str):  Column name containing the trial type information (default: 'trial_type').
    incl_trialtypes (list):  List of trial types to include; if None, all types are included, 
    modtype (str): Modality type, either 'hcp' or 'alt' for alternative processing (default: 'hcp').
    new_trialcol_name (str) : Name for the new column containing processed trial types (default: 'new_trialtype').
        
    Returns:
    Processed copy of the events dataframe with combined trial type information.
    """
    if modtype not in ["hcp", "alt"]:
        raise ValueError(f"Incorrect model provided: {modtype}. Should be 'hcp' or 'alt'")
    
    
    eventdf_cpy = eventsdf.copy()
    
    if modtype == "hcp":
        if incl_trialtypes:
            for block_type in eventdf_cpy["block_type"].unique():
                if "Back_Block" not in block_type:
                    continue
                
                block_rows = eventdf_cpy[eventdf_cpy["block_type"] == block_type]
                back_type = block_type.split("_")[0]  # Extract "2Back" from "2Back_Block1"
                
                cue_pattern = f"cue_{back_type[0]}"
                full_pattern = f"{back_type[0]}back_full"
                
                cue_rows = block_rows[block_rows[trialtype_colname].str.startswith(cue_pattern)]
                full_rows = block_rows[block_rows[trialtype_colname] == full_pattern]
                
                if not cue_rows.empty:
                    cue_row = cue_rows.iloc[0]
                    for _, full_row in full_rows.iterrows():
                        full_idx = full_row.name
                        eventdf_cpy.at[full_idx, "onset"] = cue_row["onset"]
                        eventdf_cpy.at[full_idx, "duration"] = cue_row["duration"] + full_row["duration"]
            
            eventdf_cpy = eventdf_cpy[eventdf_cpy[trialtype_colname].isin(incl_trialtypes)].copy()
            eventdf_cpy[new_trialcol_name] = eventdf_cpy.apply(
                lambda row: f"{row[trialtype_colname]}_{row['stimulus_type'].lower()}"
                if pd.notna(row["stimulus_type"]) else row[trialtype_colname], axis=1
            )
    
    elif modtype == "alt":
        if incl_trialtypes:
        
            # Add reaction time regressor rows
            eventdf_rt = add_reactiontime_regressor(
                eventsdf=eventsdf, 
                trial_type_col=trialtype_colname, 
                resp_trialtype=[
                    "2back_nonlure", "2back_target", "2back_lure", 
                    "0back_nonlure", "0back_target", "0back_lure"
                ], 
                response_colname="response_time", 
                rtreg_name="rt"
            )
            
            eventdf_cpy = eventdf_rt[eventdf_rt[trialtype_colname].isin(incl_trialtypes)].copy()
            eventdf_cpy[new_trialcol_name] = eventdf_cpy.apply(
                lambda row: f"{row[trialtype_colname]}_{row['stimulus_type'].lower()}"
                if pd.notna(row["stimulus_type"]) else row[trialtype_colname], axis=1
            )
    
    return eventdf_cpy
