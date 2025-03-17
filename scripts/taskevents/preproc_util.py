import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Union, Tuple, Optional, Any


def lang_labelblocks(df: pd.DataFrame, indicator_col: str = 'Procedure[Block]') -> pd.DataFrame:
    """
    Label emotion task blocks based on procedure markers.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing E-Prime data
    indicator_col : str, optional
        Column name containing procedure information, by default 'Procedure'
        
    Returns
    -------
    pd.DataFrame
        DataFrame with added 'Block_Label' column
    """
    df = df.copy()  # Avoid modifying the original DataFrame

    # Create a counter for each block type
    block_counters = {'Story': 0, 'Math': 0, 
                      'Dummy': 0, 'Change': 0}
    block_label = None
    block_labels = []

    for procedure in df[indicator_col]:
        # Update block label if a new block starts
        if "StoryProc" in procedure:
            block_counters['Story'] += 1
            block_label = f"Story_Block{block_counters['Story']}"
        elif "MathProc" in procedure:
            block_counters['Math'] += 1
            block_label = f"Math_Block{block_counters['Math']}"
        elif "DummyProc" in procedure:
            block_counters['Dummy'] += 1
            block_label = f"Dummy_Block{block_counters['Dummy']}"
        elif "PresentChangePROC" in procedure:
            block_counters['Change'] += 1
            block_label = f"Change_Block{block_counters['Change']}"

        # Assign current label (will persist across trials)
        block_labels.append(block_label)

    df['Block_Label'] = block_labels
    return df

def language_eprime_preproc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess E-Prime data from language task for fMRI analysis.
    
    Transforms wide-format data into long-format trial data with onset, duration, and trial type.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing E-Prime data in wide format
        
    Returns
    -------
    pd.DataFrame
        Long-format DataFrame with onset, duration, and trial type information
    """
    df_relab = lang_labelblocks(df)

    long_format = []
    
    for _, row in df_relab.iterrows():
        adjust_by_trigger = row['GetReady.OffsetTime']
        
        # Story trials
        if 'Story' in row['Procedure[Block]']:
            # Present story event
            long_format.append({
                'onset': row['PresentStoryFile.OnsetTime'] - adjust_by_trigger,
                'duration': (row['PresentStoryFile.FinishTime'] - row['PresentStoryFile.OnsetTime']),
                'trial_type': 'present_story',
                'block': row['Block_Label'],
                'response_time': np.nan,
                'accuracy': np.nan,
                'response': np.nan
            })

            # Story to question transition period
            long_format.append({
                'onset': row['PresentStoryFile.OnsetTime'] - adjust_by_trigger,
                'duration': (row['ThatWasAbout.OnsetTime'] - row['PresentStoryFile.OnsetTime']),
                'trial_type': 'story_to_question',
                'block': row['Block_Label'],
                'response_time': np.nan,
                'accuracy': np.nan,
                'response': np.nan            
            })

            # Full story period (including response)
            long_format.append({
                'onset': row['PresentStoryFile.OnsetTime'] - adjust_by_trigger,
                'duration': (row['ResponsePeriod.FinishTime'] - row['PresentStoryFile.OnsetTime']),
                'trial_type': 'full_story',
                'block': row['Block_Label'],
                'response_time': np.nan,
                'accuracy': np.nan,
                'response': np.nan
            })
            
            # "That was about" question prompt
            long_format.append({
                'onset': row['ThatWasAbout.OnsetTime'] - adjust_by_trigger,
                'duration': (row['ThatWasAbout.FinishTime'] - row['ThatWasAbout.OnsetTime']),
                'trial_type': 'question_story',
                'block': row['Block_Label'],
                'response_time': np.nan,
                'accuracy': np.nan,
                'response': np.nan
            })
            
            # Story option 1
            long_format.append({
                'onset': row['PresentStoryOption1.OnsetTime'] - adjust_by_trigger,
                'duration': (row['PresentStoryOption1.FinishTime'] - row['PresentStoryOption1.OnsetTime']),
                'trial_type': 'story_opt1',
                'block': row['Block_Label'],
                'word_opt': row['Option1'],
                'response_time': row.get('PresentStoryOption1.RT', np.nan),
                'accuracy': row.get('PresentStoryOption1.ACC', np.nan),
                'response': row.get('PresentStoryOption1.RESP', np.nan),
                'overall_acc': row.get('OverallAcc[Trial]', np.nan)
            })
            
            # Story option 2
            long_format.append({
                'onset': row['PresentStoryOption2.OnsetTime'] - adjust_by_trigger,
                'duration': (row['PresentStoryOption2.FinishTime'] - row['PresentStoryOption2.OnsetTime']),
                'trial_type': 'story_opt2',
                'word_opt': row['Option2'],
                'block': row['Block_Label'],
                'response_time': row.get('PresentStoryOption2.RT', np.nan),
                'accuracy': row.get('PresentStoryOption2.ACC', np.nan),
                'response': row.get('PresentStoryOption2.RESP', np.nan),
                'overall_acc': row.get('OverallAcc[Trial]', np.nan)
            })

            # Response period
            # cleaned up after input form Nicholas Bloom (nbloom@wustl.edu) who helped code Language tas.
            long_format.append(
                'onset': row['ResponsePeriod.OnsetTime'] - adjust_by_trigger,
                'duration': (row['ResponsePeriod.FinishTime'] - row['ResponsePeriod.OnsetTime']),
                'trial_type': 'story_answer',
                'block': row['Block_Label'],
                'response_time': row.get('FilteredTrialStats.RTFromFirstOption', np.nan), # not ResponsePeriod.RT, responses may occur earlier than period
                'filtered_rttime': row.get('FilteredTrialStats.RTTIME',np.nan),
                'accuracy': row.get('FilteredTrialStats.ACC', np.nan), # not ResposnePeriod.ACC as may iincorrectly label inacc
                'response': row.get('FilteredTrialStats.RESP', np.nan), # not ResponsePeriod.RESP as may iincorrectly label inacc
                'math_lvl': np.nan,
                'overall_acc': row.get('OverallAcc[Trial]', np.nan)
            })
            
        # Math trials
        elif 'Math' in row['Procedure[Block]']:
            # Present math file
            long_format.append({
                'onset': row['PresentMathFile.OnsetTime'] - adjust_by_trigger,
                'duration': (row['PresentMathFile.FinishTime'] - row['PresentMathFile.OnsetTime']),
                'trial_type': 'present_math',
                'block': row['Block_Label']
            })
            
            # Full math period (including response)
            long_format.append({
                'onset': row['PresentMathFile.OnsetTime'] - adjust_by_trigger,
                'duration': (row['ResponsePeriod.FinishTime'] - row['PresentMathFile.OnsetTime']),
                'trial_type': 'full_math',
                'block': row['Block_Label']
            })
            
            long_format.append({
                'onset': row['PresentMathFile.OnsetTime'] - adjust_by_trigger,
                'duration': (row['PresentMathOptions.OnsetTime'] - row['PresentMathFile.OnsetTime']),
                'trial_type': 'math_to_question',
                'block': row['Block_Label']       
            })
            
            # Math options presentation
            long_format.append({
                'onset': row['PresentMathOptions.OnsetTime'] - adjust_by_trigger,
                'duration': (row['PresentMathOptions.FinishTime'] - row['PresentMathOptions.OnsetTime']),
                'trial_type': 'question_math',
                'block': row['Block_Label'],
                'math_lvl': row.get('CurrentMathLevel[Trial]', np.nan)
            })
            
            # Math response period
            # modified per Nick
            long_format.append({
                'onset': row['ResponsePeriod.OnsetTime'] - adjust_by_trigger,
                'duration': (row['ResponsePeriod.FinishTime'] - row['ResponsePeriod.OnsetTime']),
                'trial_type': 'math_answer',
                'block': row['Block_Label'],
                'response_time': row.get('FilteredTrialStats.RTFromFirstOption', np.nan), # not ResponsePeriod.RT, responses may occur earlier than period
                'filtered_rttime': row.get('FilteredTrialStats.RTTIME',np.nan),
                'accuracy': row.get('ResponsePeriod.ACC', np.nan),
                'response': row.get('ResponsePeriod.RESP', np.nan),
                'math_lvl': row.get('CurrentMathLevel[Trial]', np.nan),
                'overall_acc': row.get('OverallAcc[Trial]', np.nan)
            })

            
        
        # Block Changes (if present)
        elif 'Change' in row['Procedure[Block]']:
            long_format.append({
                'onset': row['PresentBlockChange.OnsetTime'] - adjust_by_trigger,
                'duration': (row['PresentBlockChange.FinishTime'] - row['PresentBlockChange.OnsetTime']),
                'trial_type': 'change',
                'block': row['Block_Label'],
                'response_time': np.nan,
                'accuracy': np.nan,
                'response': np.nan
            })
    
    # Convert to DataFrame and transform time units
    long_df = pd.DataFrame(long_format)
    long_df['onset'] = long_df['onset'] / 1000  # convert to seconds
    long_df['duration'] = long_df['duration'] / 1000  # convert to seconds
    
    return long_df


def emotion_labelblocks(df: pd.DataFrame, indicator_col: str = 'Procedure') -> pd.DataFrame:
    """
    Label emotion task blocks based on procedure markers.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing E-Prime data
    indicator_col : str, optional
        Column name containing procedure information, by default 'Procedure'
        
    Returns
    -------
    pd.DataFrame
        DataFrame with added 'Block_Label' column
    """
    df = df.copy()  # Avoid modifying the original DataFrame

    # Create a counter for each block type
    block_counters = {'Shape': 0, 'Face': 0}
    block_label = None
    block_labels = []

    for procedure in df[indicator_col]:
        # Update block label if a new block starts
        if "ShapePromptPROC" in procedure:
            block_counters['Shape'] += 1
            block_label = f"Shape_Block{block_counters['Shape']}"
        elif "FacePromptPROC" in procedure:
            block_counters['Face'] += 1
            block_label = f"Face_Block{block_counters['Face']}"

        # Assign current label (will persist across trials)
        block_labels.append(block_label)

    df['Block_Label'] = block_labels
    return df


def emotion_eprime_preproc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess E-Prime data from emotion task for fMRI analysis.
    
    Transforms wide-format data into long-format with onset, duration, and trial information.
    Labels blocks and calculates block-level metrics.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing E-Prime data in wide format
        
    Returns
    -------
    pd.DataFrame
        Long-format DataFrame with trial and block information
    """
    # Label blocks first
    df_relab = emotion_labelblocks(df)
    
    long_format = []
    adjust_by_trigger = df_relab['SyncSlide.OnsetTime'].iloc[0]  # Initial sync time

    # Store previous durations for edge cases
    last_duration = None
    face_dur_last = None

    # Trial-by-trial processing
    for index in range(len(df_relab)):  
        row = df_relab.iloc[index]

        # Shape cue trials
        if row['Procedure'] == 'ShapePromptPROC':
            if index < len(df_relab) - 1:
                next_row = df_relab.iloc[index + 1]
                duration = next_row['StimSlide.OnsetTime'] - row['shape.OnsetTime']
                last_duration = duration  # Save for potential edge cases
            else:
                # If last row, use previous duration
                duration = last_duration if last_duration is not None else 1000
                
            long_format.append({
                'onset': row['shape.OnsetTime'] - adjust_by_trigger,
                'duration': duration,
                'trial_type': 'cue_shape',
                'block_type': row['Block_Label'],
                'response_time': row.get('StimSlide.RT', np.nan),
                'accuracy': row.get('StimSlide.ACC', np.nan)
            })
            
        # Face cue trials
        elif row['Procedure'] == 'FacePromptPROC':
            if index < len(df_relab) - 1:
                next_row = df_relab.iloc[index + 1]
                face_dur = next_row['StimSlide.OnsetTime'] - row['face.OnsetTime']
                face_dur_last = face_dur  # Save for potential edge cases
            else:
                # If last row, use previous duration
                face_dur = face_dur_last if face_dur_last is not None else 1000
                
            long_format.append({
                'onset': row['face.OnsetTime'] - adjust_by_trigger,
                'duration': face_dur,
                'trial_type': 'cue_face',
                'block_type': row['Block_Label'],
                'response_time': row.get('StimSlide.RT', np.nan),
                'accuracy': row.get('StimSlide.ACC', np.nan)
            })

    # Add block-level entries
    block_labels = df_relab['Block_Label'].dropna().unique()
    
    for block_label in block_labels:
        # Filter rows for this block
        block_rows = df_relab[df_relab['Block_Label'] == block_label]
        
        if len(block_rows) > 0:
            # Get first and last rows (skip cue row)
            first_row = block_rows.iloc[1]
            last_row = block_rows.iloc[-1]
            
            # Determine block type 
            block_type = "Shape" if "Shape" in block_label else "Face"
            
            # Calculate block onset and duration
            block_onset = first_row['StimSlide.OnsetTime']
            
            # Try to find end time using various methods
            if pd.notna(last_row.get('StimSlide.FinishTime')):
                block_end = last_row['StimSlide.FinishTime']
            elif pd.notna(last_row.get('StimSlide.OnsetTime')):
                # If no finish time, estimate using onset plus typical duration
                expected_dur = last_row.get('StimSlide.OnsetToOnsetTime', 1000)
                block_end = last_row['StimSlide.OnsetTime'] + expected_dur
            else:
                # Try to find start of next block
                next_idx = df_relab.index[df_relab.index > last_row.name].min()
                if pd.notna(next_idx):
                    next_row = df_relab.loc[next_idx]
                    if "Shape" in next_row.get('Block_Label', ''):
                        block_end = next_row['shape.OnsetTime']
                    else:
                        block_end = next_row['face.OnsetTime']
                else:
                    # Default if no other method works
                    block_end = block_onset + 30000  # 30 second default
            
            block_duration = block_end - block_onset
            
            # Calculate block metrics
            block_acc = block_rows['StimSlide.ACC'].mean()
            block_rt = block_rows['StimSlide.RT'].mean()
            
            # Add block entry
            long_format.append({
                'onset': block_onset - adjust_by_trigger,
                'duration': block_duration,
                'trial_type': f'{block_type.lower()}_block',
                'block_type': block_label,
                'response_time': block_rt,
                'accuracy': block_acc
            })

            # Process each trial in the block (skip first row as it's the prompt)
            for index, row in block_rows.iloc[1:].iterrows():
                # Add stimulus trial
                long_format.append({
                    'onset': row['StimSlide.OnsetTime'] - adjust_by_trigger,
                    'duration': row['StimSlide.OnsetToOnsetTime'],
                    'trial_type': f"{row['Block_Label'].split('_')[0].lower()}_stim",
                    'block_type': row['Block_Label'],
                    'response_time': row['StimSlide.RT'],
                    'accuracy': row['StimSlide.ACC']
                })
                
                # add ISI
                long_format.append({
                    'onset': row['Fixation.OnsetTime'] - adjust_by_trigger,
                    'duration': 2000, # using papers defined 2000ms, as calc between rows is meticululous and diff approx ~40-60ms
                    'trial_type': f"{row['Block_Label'].split('_')[0].lower()}_isi",
                    'block_type': row['Block_Label'],
                    'response_time': row['StimSlide.RT'],
                    'accuracy': row['StimSlide.ACC']
                })

        
    
    # Convert to DataFrame and sort by onset time
    long_df = pd.DataFrame(long_format)
    
    # Convert times from ms to seconds
    long_df['onset'] = long_df['onset'] / 1000  # convert to seconds
    long_df['duration'] = long_df['duration'] / 1000  # convert to seconds
    
    # Sort events by onset time
    long_df = long_df.sort_values(by='onset').reset_index(drop=True)
    
    return long_df


def wm_labelblocks(df: pd.DataFrame, indicator_col: str = 'Procedure[Block]') -> pd.DataFrame:
    """
    Label working memory task blocks based on procedure markers.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing E-Prime data
    indicator_col : str, optional
        Column name containing procedure information, by default 'Procedure[Block]'
        
    Returns
    -------
    pd.DataFrame
        DataFrame with added 'Block_Label' column
    """
    df = df.copy()  # Avoid modifying the original DataFrame
    
    # Create a counter for each block type
    block_counters = {'2Back': 0, '0Back': 0, 'Fix': 0}
    block_label = None  
    block_labels = []
    
    for procedure in df[indicator_col]:
        # Update block label if a new block starts
        if "Cue2BackPROC" in procedure:
            block_counters['2Back'] += 1
            block_label = f"2Back_Block{block_counters['2Back']}"
        elif "Cue0BackPROC" in procedure:
            block_counters['0Back'] += 1
            block_label = f"0Back_Block{block_counters['0Back']}"
        elif "Fix15secPROC" in procedure:
            block_counters['Fix'] += 1
            block_label = f"Fix_Block{block_counters['Fix']}"
        
        # Assign current label
        block_labels.append(block_label)
    
    df['Block_Label'] = block_labels
    return df


def wm_eprime_preproc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess E-Prime data from working memory task for fMRI analysis.
    
    Transforms wide-format data into long-format with onset, duration, and trial information.
    Labels blocks and calculates block-level metrics.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing E-Prime data in wide format
        
    Returns
    -------
    pd.DataFrame
        Long-format DataFrame with trial and block information
    """
    # Label blocks first
    df_relab = wm_labelblocks(df)
    
    long_format = []
    adjust_by_trigger = df_relab['SyncSlide.OnsetTime'].iloc[0]  # Initial sync time

    # Store previous durations for edge cases
    last_duration = None
    back2_dur_last = None

    # Trial-by-trial processing
    for index in range(len(df_relab)):  
        row = df_relab.iloc[index]

        # 0-back cue trials
        if row['Procedure[Block]'] == 'Cue0BackPROC':
            if index < len(df_relab) - 1:
                next_row = df_relab.iloc[index + 1]
                duration = next_row['Stim.OnsetTime'] - row['CueTarget.OnsetTime']
                last_duration = duration
            else:
                duration = last_duration if last_duration is not None else 2000
                
            long_format.append({
                'onset': row['CueTarget.OnsetTime'] - adjust_by_trigger,
                'duration': duration,
                'trial_type': 'cue_0back',
                'block_type': row['Block_Label'],
                'stimulus_type': row['StimType'],
                'response_time': row.get('Stim.RT', np.nan),
                'accuracy': row.get('Stim.ACC', np.nan)
            })
            
        # 2-back cue trials
        elif row['Procedure[Block]'] == 'Cue2BackPROC':
            if index < len(df_relab) - 1:
                next_row = df_relab.iloc[index + 1]
                back2_dur = next_row['Stim.OnsetTime'] - row['Cue2Back.OnsetTime']
                back2_dur_last = back2_dur
            else:
                back2_dur = back2_dur_last if back2_dur_last is not None else 2000
                
            long_format.append({
                'onset': row['Cue2Back.OnsetTime'] - adjust_by_trigger,
                'duration': back2_dur,
                'trial_type': 'cue_2back',
                'block_type': row['Block_Label'],
                'stimulus_type': row['StimType'],
                'response_time': row.get('Stim.RT', np.nan),
                'accuracy': row.get('Stim.ACC', np.nan)
            })
        
        # Fixation blocks
        elif row['Procedure[Block]'] == 'Fix15secPROC':
            long_format.append({
                'onset': row['Fix15sec.OnsetTime'] - adjust_by_trigger,
                'duration': 15000,  # Fixed 15s fixation duration
                'trial_type': 'fixation',
                'block_type': row['Block_Label'],
                'response_time': row.get('Stim.RT', np.nan),
                'accuracy': row.get('Stim.ACC', np.nan)
            })

    # Add block-level entries
    block_labels = df_relab['Block_Label'].dropna().unique()
    
    for block_label in block_labels:
        # Skip fixation blocks for block-level analysis
        if "Fix_Block" in block_label:
            continue
            
        # Filter rows for this block
        block_rows = df_relab[df_relab['Block_Label'] == block_label]
        
        if len(block_rows) > 0:
            # Get the main rows (skip cue row)
            first_row = block_rows.iloc[1]
            last_row = block_rows.iloc[-1]
            
            # Determine block type
            block_type = "0Back" if "0Back" in block_label else "2Back"
            
            # Calculate block timing
            block_onset = first_row['Stim.OnsetTime']
            
            # Try to determine end time
            if pd.notna(last_row.get('Stim.OnsetTime')):
                block_end = last_row['Stim.OnsetTime'] + last_row['Stim.OnsetToOnsetTime']
            else:
                # Fallback if not available
                expected_dur = last_row.get('Stim.OnsetTime', 2000)
                block_end = last_row['Stim.OnsetTime'] + expected_dur

            block_duration = block_end - block_onset
            
            # Calculate block metrics
            block_acc = block_rows['Stim.ACC'].mean()
            block_rt = block_rows['Stim.RT'].mean()
            
            # Add block-level entry
            long_format.append({
                'onset': block_onset - adjust_by_trigger,
                'duration': block_duration,
                'trial_type': f'{block_type.lower()}_full',
                'block_type': block_label,
                'stimulus_type': first_row['StimType'],
                'response_time': block_rt,
                'accuracy': block_acc
            })
            
            # Add trial-level entries within blocks
            if block_type in ["0Back", "2Back"]:
                # Skip the cue (first row)
                for i, row in block_rows.iloc[1:].iterrows():
                    if 'TargetType' in row:
                        # Calculate trial timing
                        trial_onset = row['Stim.OnsetTime']
                        
                        # Use OnsetToOnsetTime if available, otherwise use default
                        trial_duration = row.get('Stim.OnsetToOnsetTime', 2000)
                        
                        # Add trial entry
                        long_format.append({
                            'onset': trial_onset - adjust_by_trigger,
                            'duration': trial_duration,
                            'trial_type': f'{block_type.lower()}_{row["TargetType"].lower()}',
                            'block_type': block_label,
                            'stimulus_type': row['StimType'],
                            'target_type': row['TargetType'],
                            'response_time': row['Stim.RT'] if pd.notna(row.get('Stim.RT')) else None,
                            'accuracy': row['Stim.ACC'] if pd.notna(row.get('Stim.ACC')) else None
                        })
    
    # Convert to DataFrame and process times
    long_df = pd.DataFrame(long_format)
    
    # Convert times from ms to seconds
    long_df['onset'] = long_df['onset'] / 1000  # convert to seconds
    long_df['duration'] = long_df['duration'] / 1000  # convert to seconds
    
    # Sort by onset time
    long_df = long_df.sort_values(by='onset').reset_index(drop=True)
    
    return long_df


def motor_labelblocks(df: pd.DataFrame, indicator_col: str = 'Procedure[Trial]') -> pd.DataFrame:
    """
    Labels blocks in the DataFrame based on motor procedure markers.
    
    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the procedure information.
    indicator_col : str, optional
        The column name that contains procedure types, by default 'Procedure[Trial]'
    
    Returns
    -------
    pd.DataFrame
        A copy of the original DataFrame with an additional 'Block_Label' column
        that identifies the block type and number (e.g., 'LeftHand_Block1').
    """
    df = df.copy()  # Avoid modifying the original DataFrame
    
    # Create a counter for each type
    block_counters = {
        'LeftHand': 0, 
        'RightHand': 0,
        'LeftFoot': 0, 
        'RightFoot': 0,
        'Tongue': 0, 
        'Fix': 0
    }
    block_label = None
    block_labels = []

    for procedure in df[indicator_col].fillna(""):
        if "LeftHand" in procedure:
            block_counters['LeftHand'] += 1
            block_label = f"LeftHand_Block{block_counters['LeftHand']}"
        elif "RightHand" in procedure:
            block_counters['RightHand'] += 1
            block_label = f"RightHand_Block{block_counters['RightHand']}"
        elif "LeftFoot" in procedure:
            block_counters['LeftFoot'] += 1
            block_label = f"LeftFoot_Block{block_counters['LeftFoot']}"
        elif "RightFoot" in procedure:
            block_counters['RightFoot'] += 1
            block_label = f"RightFoot_Block{block_counters['RightFoot']}"
        elif "Tongue" in procedure:
            block_counters['Tongue'] += 1
            block_label = f"Tongue_Block{block_counters['Tongue']}"
        elif "Fix" in procedure:
            block_counters['Fix'] += 1
            block_label = f"Fix_Block{block_counters['Fix']}"
        
        # Assign the current label
        block_labels.append(block_label)

    df['Block_Label'] = block_labels
    return df


def motor_eprime_preproc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess E-Prime output data from a motor experiment into a long-format DataFrame.
    
    This function processes motor experiment data, including left/right hand/foot and tongue
    movement cues. It creates trial-by-trial entries and block-level entries in the resulting
    DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw E-Prime output data containing motor experiment information.
    
    Returns
    -------
    pd.DataFrame
        Long-format DataFrame with columns:
        - onset: onset time in seconds
        - duration: duration in seconds
        - trial_type: type of trial (e.g., 'cue_LeftHand', 'lefthand')
        - block_type: block label
    
    Notes
    -----
    The function first labels blocks using motor_labelblocks() and then:
    1. Processes individual trial events (cues)
    2. Adds block-level entries with onset/duration for each motor movement type
    3. Converts times from milliseconds to seconds
    4. Sorts entries by onset time
    """
    # Label blocks in the DataFrame
    df_relab = motor_labelblocks(df)
    
    # Initialize list to store long format data
    long_format = []
    
    # Get the reference time point for adjusting onset times
    adjust_by_trigger = df_relab['CountDownSlide.OnsetTime'][0]
    
    # Process trial-by-trial data
    for index in range(len(df_relab)):
        row = df_relab.iloc[index]

        # Process different types of cue trials
        if row['Procedure[Trial]'] == 'LeftHandCueProcedure':
            next_row = df_relab.iloc[index + 1]
            duration = next_row['CrossLeft.OnsetTime'] - row['LeftHandCue.OnsetTime']
            
            long_format.append({
                'onset': row['LeftHandCue.OnsetTime'] - adjust_by_trigger,
                'duration': duration,
                'trial_type': 'cue_lefthand',
                'block_type': row['Block_Label']
            })
        elif row['Procedure[Trial]'] == 'RightHandCuePROC':
            next_row = df_relab.iloc[index + 1]
            duration = next_row['CrossRight.OnsetTime'] - row['RightHandCue.OnsetTime']
            
            long_format.append({
                'onset': row['RightHandCue.OnsetTime'] - adjust_by_trigger,
                'duration': duration,
                'trial_type': 'cue_righthand',
                'block_type': row['Block_Label']
            })
        elif row['Procedure[Trial]'] == 'LeftFootCuePROC':
            next_row = df_relab.iloc[index + 1]
            duration = next_row['CrossLeft.OnsetTime'] - row['LeftFootCue.OnsetTime']
            
            long_format.append({
                'onset': row['LeftFootCue.OnsetTime'] - adjust_by_trigger,
                'duration': duration,
                'trial_type': 'cue_leftfoot',
                'block_type': row['Block_Label']
            })
        elif row['Procedure[Trial]'] == 'RightFoottCuePROC':
            next_row = df_relab.iloc[index + 1]
            duration = next_row['CrossRight.OnsetTime'] - row['RightFootCue.OnsetTime']
            
            long_format.append({
                'onset': row['RightFootCue.OnsetTime'] - adjust_by_trigger,
                'duration': duration,
                'trial_type': 'cue_rightfoot',
                'block_type': row['Block_Label']
            })
        elif row['Procedure[Trial]'] == 'TongueCuePROC':
            next_row = df_relab.iloc[index + 1]
            duration = next_row['CrossCenter.OnsetTime'] - row['TongueCue.OnsetTime']
            
            long_format.append({
                'onset': row['TongueCue.OnsetTime'] - adjust_by_trigger,
                'duration': duration,
                'trial_type': 'cue_tongue',
                'block_type': row['Block_Label']
            })
        elif row['Procedure[Trial]'] == 'FixPROC':
            long_format.append({
                'onset': row['Fixdot.OnsetTime'] - adjust_by_trigger,
                'duration': 18000, # default per paper
                'trial_type': 'fixation',
                'block_type': row['Block_Label']
            })

    # Add block-level entries
    block_labels = df_relab['Block_Label'].dropna().unique()
    
    for block_label in block_labels:
        if "Fix_Block" in block_label:
            continue
            
        # Filter rows for this block
        block_rows = df_relab[df_relab['Block_Label'] == block_label]
        
        if len(block_rows) > 0:
            # Get first and last row in block. Since Cue is row one for block
            first_row = block_rows.iloc[1]
            last_row = block_rows.iloc[-1]
            
            # Determine block type
            block_type = first_row['Block_Label'].split("_")[0]
            
            # Calculate block onset and duration based on block type
            if "LeftHand" in block_label:
                onsetblock = first_row['CrossLeft.OnsetTime'] - adjust_by_trigger
                durationblock = (last_row['BLANK.OnsetTime'] + 1000) - first_row['CrossLeft.OnsetTime']
            elif "RightHand" in block_label:
                onsetblock = first_row['CrossRight.OnsetTime'] - adjust_by_trigger
                durationblock = (last_row['BLANK.OnsetTime'] + 1000) - first_row['CrossRight.OnsetTime']
            elif "LeftFoot" in block_label:
                onsetblock = first_row['CrossLeft.OnsetTime'] - adjust_by_trigger
                durationblock = (last_row['BLANK.OnsetTime'] + 1000) - first_row['CrossLeft.OnsetTime']
            elif "RightFoot" in block_label:
                onsetblock = first_row['CrossRight.OnsetTime'] - adjust_by_trigger
                durationblock = (last_row['BLANK.OnsetTime'] + 1000) - first_row['CrossRight.OnsetTime']
            elif "Tongue" in block_label:
                onsetblock = first_row['CrossCenter.OnsetTime'] - adjust_by_trigger
                durationblock = (last_row['BLANK.OnsetTime'] + 1000) - first_row['CrossCenter.OnsetTime']
            
            # Add block entry
            long_format.append({
                'onset': onsetblock,
                'duration': durationblock,
                'trial_type': f'{block_type.lower()}',
                'block_type': first_row['Block_Label']
            })
    
    # Convert list to DataFrame and process times
    long_df = pd.DataFrame(long_format)
    
    long_df['onset'] = long_df['onset'] / 1000  # convert to seconds
    long_df['duration'] = long_df['duration'] / 1000  # convert to seconds
    
    
    # Sort and reset index
    long_df = long_df.sort_values(by='onset')
    long_df = long_df.reset_index(drop=True)
    
    return long_df


def social_eprime_preproc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess E-Prime output data from a social experiment into a long-format DataFrame.
    
    This function processes social experiment data, extracting trial information for 
    response slides, movie slides, social interactions, and fixation blocks.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw E-Prime output data containing social experiment information.
    
    Returns
    -------
    pd.DataFrame
        Long-format DataFrame with columns:
        - onset: onset time in seconds
        - duration: duration in seconds
        - trial_type: type of trial ('response', 'movie', 'social_full', 'fixation')
        - social_type: type of social interaction if applicable
        - response_time: participant response time in seconds
        - accuracy: response accuracy
        - response: participant's response
    
    Notes
    -----
    The function extracts three event types for each social trial:
    1. Response events (participant responses)
    2. Movie events (stimulus presentation)
    3. Full social trial events (movie + response)
    
    It also processes fixation blocks between trials.
    All times are converted from milliseconds to seconds.
    """
    # Initialize list to store long format data
    long_format = []
    
    # Get the reference time point for adjusting onset times
    adjust_by_trigger = df['CountDownSlide.OnsetTime'][0]
    
    # Process each row in the input DataFrame
    for index, row in df.iterrows():
        # Social trials
        if row['Procedure'] == 'SOCIALrunPROC':
            # Add response event
            long_format.append({
                'onset': row['ResponseSlide.OnsetTime'] - adjust_by_trigger,
                'duration': row['ResponseSlide.OnsetToOnsetTime'],
                'trial_type': 'response',
                'social_type': row.get('Type', np.nan),
                'response_time': row.get('ResponseSlide.RT', np.nan),
                'accuracy': row.get('ResponseSlide.ACC', np.nan),
                'response': row.get('ResponseSlide.RESP', np.nan)
            })
            
            # Add movie event
            long_format.append({
                'onset': row['MovieSlide.OnsetTime'] - adjust_by_trigger,
                'duration': row['MovieSlide.OnsetToOnsetTime'],
                'trial_type': 'movie',
                'social_type': row.get('Type', np.nan),
                'response_time': np.nan,
                'accuracy': np.nan,
                'response': np.nan
            })
            
            # Add full social trial event (movie + response)
            long_format.append({
                'onset': row['MovieSlide.OnsetTime'] - adjust_by_trigger,
                'duration': (row['ResponseSlide.OnsetTime'] + row['ResponseSlide.OnsetToOnsetTime']) - row['MovieSlide.OnsetTime'],
                'trial_type': 'social_full',
                'social_type': row.get('Type', np.nan),
                'response_time': row.get('ResponseSlide.RT', np.nan),
                'accuracy': row.get('ResponseSlide.ACC', np.nan),
                'response': row.get('ResponseSlide.RESP', np.nan)
            })

        # Fixation blocks
        elif row['Procedure'] == 'FixationBlockPROC':
            # Find the onset time of the next movie slide
            next_movie_row = df.loc[index+1:, 'MovieSlide.OnsetTime'].dropna()
            next_movie_onset = next_movie_row.iloc[0] if not next_movie_row.empty else None
            
            # Calculate duration (use default of 15s if no next movie)
            duration = next_movie_onset - row['FixationBlock.OnsetTime'] if next_movie_onset is not None else 15000
            
            # Add fixation block event
            long_format.append({
                'onset': row['FixationBlock.OnsetTime'] - adjust_by_trigger,
                'duration': duration,
                'trial_type': 'fixation',
                'social_type': np.nan,
                'response_time': np.nan,
                'accuracy': np.nan,
                'response': np.nan
            })
    
    # Convert list to DataFrame and process times
    long_df = pd.DataFrame(long_format)
    long_df['onset'] = long_df['onset'] / 1000        # convert to seconds
    long_df['duration'] = long_df['duration'] / 1000  # convert to seconds
    
    # Sort and reset index
    long_df = long_df.sort_values(by='onset')
    long_df = long_df.reset_index(drop=True)
    
    return long_df


def relational_labelblocks(df: pd.DataFrame, indicator_col: str = 'Procedure') -> pd.DataFrame:
    """
    Labels blocks in the DataFrame based on relational experiment procedure markers.
    
    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing procedure information.
    indicator_col : str, optional
        The column name that contains procedure types, by default 'Procedure'
    
    Returns
    -------
    pd.DataFrame
        A copy of the original DataFrame with an additional 'Block_Label' column
        that identifies the block type and number (e.g., 'Relation_Block1',
        'Control_Block1', 'Fix_Block1').
    """
    df = df.copy()  # Avoid modifying the original DataFrame
    
    # Create a counter for each block type
    block_counters = {'Relational': 0, 'Control': 0, 'Fix': 0}
    block_label = None  
    block_labels = []

    # Process each procedure and assign a block label
    for procedure in df[indicator_col].fillna(""):
        if "RelationalPromptPROC" in procedure:
            block_counters['Relational'] += 1
            block_label = f"Relation_Block{block_counters['Relational']}"
        elif "ControlPromptPROC" in procedure:
            block_counters['Control'] += 1
            block_label = f"Control_Block{block_counters['Control']}"
        elif "FixationPROC" in procedure:
            block_counters['Fix'] += 1
            block_label = f"Fix_Block{block_counters['Fix']}"
            
        # Append the current label to the list
        block_labels.append(block_label)

    # Add block labels to the DataFrame
    df['Block_Label'] = block_labels
    return df


def relation_eprime_preproc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess E-Prime output data from a relational experiment into a long-format DataFrame.
    
    This function processes relational reasoning experiment data, extracting information
    about relational and control trials, including prompts, stimuli, responses, and
    fixation blocks.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw E-Prime output data containing relational experiment information.
    
    Returns
    -------
    pd.DataFrame
        Long-format DataFrame with columns:
        - onset: onset time in seconds
        - duration: duration in seconds
        - trial_type: type of trial ('relation_prompt', 'control_prompt', 'fix_block', etc.)
        - stim_type: type of stimulus if applicable
        - response_time: participant response time in seconds
        - block: block label
        - accuracy: response accuracy
        - response: participant's response
    
    Notes
    -----
    The function first labels blocks using relational_labelblocks(), then:
    1. Processes individual trial events (prompts, fixations)
    2. Adds block-level and trial-level entries for relational and control blocks
    3. Includes detailed stimulus, response, and accuracy information
    4. Converts times from milliseconds to seconds
    5. Sorts entries by onset time
    """
    # Label blocks in the DataFrame
    df_relab = relational_labelblocks(df)
    
    # Initialize list to store long format data
    long_format = []
    
    # Get the reference time point for adjusting onset times
    adjust_by_trigger = df_relab['SyncSlide.OnsetTime'][0]
    
    # Process each row in the input DataFrame
    for index, row in df_relab.iterrows():
        # Relational prompt trials
        if row['Procedure'] == 'RelationalPromptPROC':
            long_format.append({
                'onset': row['RelationalPrompt.OnsetTime'] - adjust_by_trigger,
                'duration': row['RelationalPrompt.OffsetTime'] - row['RelationalPrompt.OnsetTime'],
                'trial_type': 'relation_prompt',
                'stim_type': np.nan,
                'response_time': np.nan,
                'block': row['Block_Label'],
                'accuracy': np.nan,
                'response': np.nan
            })
        
        # Control prompt trials    
        elif row['Procedure'] == 'ControlPromptPROC':
            long_format.append({
                'onset': row['ControlPrompt.OnsetTime'] - adjust_by_trigger,
                'duration': row['ControlPrompt.OffsetTime'] - row['ControlPrompt.OnsetTime'],
                'trial_type': 'control_prompt',
                'stim_type': np.nan,
                'response_time': np.nan,
                'block': row['Block_Label'],
                'accuracy': np.nan,
                'response': np.nan
            })

        # Fixation blocks
        elif row['Procedure'] == 'FixationPROC':
            long_format.append({
                'onset': row['FixationBlock.OnsetTime'] - adjust_by_trigger,
                'duration': row['FixationBlock.FinishTime'] - row['FixationBlock.OnsetTime'],
                'trial_type': 'fix_block',
                'stim_type': np.nan,
                'response_time': np.nan,
                'block': row['Block_Label'],
                'accuracy': np.nan,
                'response': np.nan
            })

    # Process block-level and trial-level entries
    block_labels = df_relab['Block_Label'].dropna().unique()
    
    for block_label in block_labels:
        # Skip fixation blocks
        if "Fix_Block" in block_label:
            continue
            
        # Filter rows for this block
        block_rows = df_relab[df_relab['Block_Label'] == block_label]
        
        # Get first and last row in block (skip first row as it's the prompt)
        first_row = block_rows.iloc[1]
        last_row = block_rows.iloc[-1]
        
        # Process relational blocks
        if "Relation_Block" in block_label:
            # Calculate block onset and duration
            onset_rel_block = first_row['RelationalSlide.OnsetTime']
            end_rel_block = last_row['RelationalBlank.FinishTime']
            
            # Add block-level entry
            long_format.append({
                'onset': onset_rel_block - adjust_by_trigger,
                'duration': end_rel_block - onset_rel_block,
                'trial_type': 'relation_block',
                'stim_type': np.nan,
                'response_time': block_rows['RelationalSlide.RT'].mean(),
                'block': first_row['Block_Label'],
                'accuracy': block_rows['RelationalSlide.ACC'].mean(),
                'response': np.nan
            })
            
            # Process each trial in the block (skip first row as it's the prompt)
            for index, row in block_rows.iloc[1:].iterrows():
                # Add stimulus trial
                long_format.append({
                    'onset': row['RelationalSlide.OnsetTime'] - adjust_by_trigger,
                    'duration': row['RelationalSlide.FinishTime'] - row['RelationalSlide.OnsetTime'],
                    'trial_type': 'relation_stim',
                    'stim_type': row['Instruction'],
                    'response_time': row['RelationalSlide.RT'],
                    'block': row['Block_Label'],
                    'accuracy': row['RelationalSlide.ACC'],
                    'response': row['RelationalSlide.RESP']
                })
                
                # Add blank/ISI trial
                long_format.append({
                    'onset': row['RelationalBlank.OnsetTime'] - adjust_by_trigger,
                    'duration': row['RelationalBlank.OnsetToOnsetTime'],
                    'trial_type': 'relation_blank',
                    'stim_type': row['Instruction'],
                    'response_time': np.nan,
                    'block': row['Block_Label'],
                    'accuracy': np.nan,
                    'response': np.nan
                })
        
        # Process control blocks      
        elif "Control_Block" in block_label:
            # Calculate block onset and duration
            onset_rel_block = first_row['ControlSlide.OnsetTime']
            end_rel_block = last_row['ControlBlank.FinishTime']
            
            # Add block-level entry
            long_format.append({
                'onset': onset_rel_block - adjust_by_trigger,
                'duration': end_rel_block - onset_rel_block,
                'trial_type': 'control_block',
                'stim_type': np.nan,
                'response_time': block_rows['ControlSlide.RT'].mean(),
                'block': first_row['Block_Label'],
                'accuracy': block_rows['ControlSlide.ACC'].mean(),
                'response': np.nan
            })

            # Process each trial in the block (skip first row as it's the prompt)
            for index, row in block_rows.iloc[1:].iterrows():
                # Add stimulus trial
                long_format.append({
                    'onset': row['ControlSlide.OnsetTime'] - adjust_by_trigger,
                    'duration': row['ControlSlide.FinishTime'] - row['ControlSlide.OnsetTime'],
                    'trial_type': 'control_stim',
                    'stim_type': row['Instruction'],
                    'response_time': row['ControlSlide.RT'],
                    'block': row['Block_Label'],
                    'accuracy': row['ControlSlide.ACC'],
                    'response': row['ControlSlide.RESP']
                })
                
                # Add blank/ISI trial
                long_format.append({
                    'onset': row['ControlBlank.OnsetTime'] - adjust_by_trigger,
                    'duration': row['ControlBlank.OnsetToOnsetTime'],
                    'trial_type': 'control_blank',
                    'stim_type': row['Instruction'],
                    'response_time': np.nan,
                    'block': row['Block_Label'],
                    'accuracy': np.nan,
                    'response': np.nan
                })

    # Convert list to DataFrame and process times
    long_df = pd.DataFrame(long_format)
    long_df['onset'] = long_df['onset'] / 1000  # convert to seconds
    long_df['duration'] = long_df['duration'] / 1000  # convert to seconds
    
    # Sort and reset index
    long_df = long_df.sort_values(by='onset')
    long_df = long_df.reset_index(drop=True)
    
    return long_df


def gamble_labelblocks(df: pd.DataFrame, indicator_col: str = 'Procedure[Trial]') -> pd.DataFrame:
    """
    Labels blocks in the DataFrame based on gambling experiment procedure markers.
    
    This function identifies blocks in the experiment by detecting transitions between
    different procedure types. It expects to find 4 gambling blocks interspersed with
    fixation blocks.
    
    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing procedure information.
    indicator_col : str, optional
        The column name that contains procedure types, by default 'Procedure[Trial]'
    
    Returns
    -------
    pd.DataFrame
        A copy of the original DataFrame with an additional 'Block_Label' column
        that identifies the block type and number (e.g., 'Gamble_Block1', 'Fix_Block1').
    """
    df = df.copy()  # Avoid modifying the original DataFrame
    
    # Create a counter for each block type
    block_counters = {'Gamble': 0, 'Fix': 0}
    block_labels = []
    
    # Track the current block type to detect transitions
    current_block_type = None
    current_block_label = None

    # Process each procedure and assign a block label
    for procedure in df[indicator_col].fillna(""):
        if "GamblingTrialPROC" in procedure:
            # Only increment counter when transitioning from a different block type
            if current_block_type != 'Gamble':
                block_counters['Gamble'] += 1
                current_block_type = 'Gamble'
                current_block_label = f"Gamble_Block{block_counters['Gamble']}"
        elif "FixationBlockPROC" in procedure:
            # Only increment counter when transitioning from a different block type
            if current_block_type != 'Fix':
                block_counters['Fix'] += 1
                current_block_type = 'Fix'
                current_block_label = f"Fix_Block{block_counters['Fix']}"
        else:
            # For any other procedure type, don't change the current block
            pass
            
        # Append the current label to the list
        block_labels.append(current_block_label)

    # Add block labels to the DataFrame
    df['Block_Label'] = block_labels
    return df


def gamble_eprime_preproc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess E-Prime output data from a gambling experiment into a long-format DataFrame.
    
    This function processes gambling experiment data, extracting information
    about trials, prompts, stimuli, responses, and fixation blocks.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw E-Prime output data containing gambling experiment information.
    
    Returns
    -------
    pd.DataFrame
        Processed data in long format with trial information.
    """
    # Label blocks in the DataFrame
    df_relab = gamble_labelblocks(df)
    
    # Initialize list to store long format data
    long_format = []
    
    # Get the reference time point for adjusting onset times
    adjust_by_trigger = df_relab['SyncSlide.OnsetTime'][0]
    
    # Process each row in the input DataFrame
    for index, row in df_relab.iterrows():
        # Gambling trials
        if row['Procedure[Trial]'] == 'GamblingTrialPROC':
            
            # sometimes the first row has 0 for onset / durations, this accounts for it.
            if row['FillerFixation.OnsetTime'] not in [0, None]:
                quest_duration = row['FillerFixation.OnsetTime'] - row['QuestionMark.OnsetTime']
                filler_onset = row['FillerFixation.OnsetTime'] - adjust_by_trigger
                filler_duration = row['FillerFixation.OnsetToOnsetTime']
            else:
                quest_duration = row['QuestionMark.OnsetToOnsetTime']
                filler_onset = 0
                filler_duration = 0
     
            long_format.append({
                'onset': row['QuestionMark.OnsetTime'] - adjust_by_trigger,
                'duration': quest_duration,
                'trial_type': 'quest_mark',
                'reward_type': row['TrialType'],
                'response_time': row['QuestionMark.RT'],
                'accuracy': row['QuestionMark.ACC'],
                'response': row['QuestionMark.RESP'],
                'feedback_type': np.nan,
                'block': row['Block_Label']
            })
            long_format.append({
                'onset': filler_onset,
                'duration': filler_duration,
                'trial_type': 'filler',
                'reward_type': row['TrialType'],
                'response_time': row['QuestionMark.RT'],
                'accuracy': np.nan,
                'response': np.nan,
                'feedback_type': np.nan,
                'block': row['Block_Label']
            })

            # sometimes the first row has 0 for onset / durations, this accounts for it.
            if row['Feedback.OnsetTime'] not in [0, None]:
                fb_onset = row['Feedback.OnsetTime'] - adjust_by_trigger
                fb_duration = row['Feedback.OnsetToOnsetTime']
            else:
                fb_onset = 0
                fb_duration = 0
                
            long_format.append({
                'onset': fb_onset,
                'duration': fb_duration,
                'trial_type': 'feedback',
                'reward_type': row['TrialType'],
                'response_time': np.nan,
                'accuracy': np.nan,
                'response': np.nan,
                'feedback_type': row['FeedbackNumber'],
                'block': row['Block_Label']
            })
            
            next_row_index = index + 1
            if next_row_index < len(df_relab) and df_relab.loc[next_row_index, 'Procedure[Trial]'] == 'GamblingTrialPROC':
                # If there's a next row and it's a gambling trial
                fix1sec_duration = df_relab.loc[next_row_index, 'QuestionMark.OnsetTime'] - row['OneSecFixation.OnsetTime']
            else:
                # no next row, using default in paper, 1000
                fix1sec_duration = 1000
        
            long_format.append({
                'onset': row['OneSecFixation.OnsetTime'] - adjust_by_trigger,
                'duration': fix1sec_duration,
                'trial_type': 'isi_1sec',
                'reward_type': row['TrialType'],
                'response_time': np.nan,
                'accuracy': np.nan,
                'response': np.nan,
                'feedback_type': np.nan,
                'block': row['Block_Label']
            })
        elif row['Procedure[Trial]'] == 'FixationBlockPROC':
            next_row_index = index + 1
            if next_row_index < len(df_relab) and df_relab.loc[next_row_index, 'Procedure[Trial]'] == 'GamblingTrialPROC':
                # If there's a next row and it's a gambling trial
                fix_duration = df_relab.loc[next_row_index, 'QuestionMark.OnsetTime'] - row['FifteenSecFixation.OnsetTime']
            else:
                # no next row, using default in paper, 15000
                fix_duration = 15000
                
            long_format.append({
                'onset': row['FifteenSecFixation.OnsetTime'] - adjust_by_trigger,
                'duration': fix_duration,
                'trial_type': 'fixation',
                'reward_type': np.nan,
                'response_time': np.nan,
                'accuracy': np.nan,
                'response': np.nan,
                'feedback_type': np.nan,
                'block': row['Block_Label']
            })

    # Convert list to DataFrame
    long_df = pd.DataFrame(long_format)

    # Process blocks to add full_gamble entries and reward/punishment proportions
    block_labels = df_relab['Block_Label'].dropna().unique()
    full_gamble_rows = []  # Store full_gamble entries separately
    
    # Calculate reward/punishment proportions for each block & full gamble blocks
    for block_label in block_labels:
        # Skip fixation blocks
        if "Fix_Block" in block_label:
            continue
            
        # Get all trials in this block
        block_trials = long_df[long_df['block'] == block_label]
        
        # Count rewards and punishments
        reward_count = sum(block_trials['reward_type'] == 'Reward')
        punish_count = sum(block_trials['reward_type'] == 'Punishment')
        
        # Determine if block is mostly reward or punishment
        mostly_reward = 1 if reward_count > punish_count else 0
        mostly_punish = 1 if punish_count > reward_count else 0
        
        # Add these flags to all rows with this block
        long_df.loc[long_df['block'] == block_label, 'mostly_reward'] = mostly_reward
        long_df.loc[long_df['block'] == block_label, 'mostly_punish'] = mostly_punish

        # full block onset/ duration
        # Filter rows for this block
        block_rows = df_relab[df_relab['Block_Label'] == block_label]
        
        # Get first and last row in block (skip first row as it's the prompt)
        if len(block_rows) > 1:  # Ensure there are at least 2 rows
            first_row = block_rows.iloc[0]
            last_row = block_rows.iloc[-1]
            
            full_gamble_rows.append({
                'onset': first_row['QuestionMark.OnsetTime'] - adjust_by_trigger,
                'duration': (last_row['Feedback.OnsetTime'] + last_row['Feedback.OnsetToOnsetTime']) - first_row['QuestionMark.OnsetTime'],
                'trial_type': 'full_gamble',
                'reward_type': np.nan,
                'response_time': np.nan,
                'accuracy': np.nan,
                'response': np.nan,
                'feedback_type': np.nan,
                'block': first_row['Block_Label'],
                'mostly_reward': mostly_reward,
                'mostly_punish': mostly_punish
            })
    
    # Add full_gamble rows to the DataFrame
    if full_gamble_rows:
        full_gamble_df = pd.DataFrame(full_gamble_rows)
        long_df = pd.concat([long_df, full_gamble_df], ignore_index=True)
    
    # Convert times to seconds
    long_df['onset'] = long_df['onset'] / 1000  # convert to seconds
    long_df['duration'] = long_df['duration'] / 1000  # convert to seconds
    
    # Sort and reset index
    long_df = long_df.sort_values(by='onset')
    long_df = long_df.reset_index(drop=True)
    
    return long_df