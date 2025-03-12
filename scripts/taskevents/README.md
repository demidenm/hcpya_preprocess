# Converting HCP E-Prime Task Timings to BIDS

The scripts here helpl download and convert the openly-available HCP E-Prime data to BIDS-specified events.tsv files. 

## Setting up AWS

Before being able to download the eprime data, you will need to setup your AWS Client.

```bash
pip install awscli
```

After install the AWS Client, run the below to configure your HCP credentials. (Note: I specify the profile here just in case you have different credentials). The configurations step will ask for (1) Access Key and (2) secret key for HCP. To obtain these, you will need to login to your setup [HCP account](https://db.humanconnectome.org/app/template/Login.vm). Once logged in, within the *WU-Minn HCP Data - 1200 Subjects* section, click on **Amazon S3 Access Enabled**. Here, you can create and copy and pase your (1) Access Key ID and (2) Secret Access key. You ID will always be available but the secret key will not, so store the latter as needed. You can always recreate it if you have forgotten yours.

```bash
aws configure --profile hcp
```

Once you have the configuration setup, you should double check your profile in your credentials and configation file:

```bash
# configuration
nano ~/.aws/config
```

```bash
# credentials
nano ~/.aws/credentials
```

The `~/.aws/config` file may look like the following. Adding `s3 part` will optimize S3 transfer performance:

```
[profile hcp]
s3 =
  max_concurrent_requests = 20
  max_queue_size = 30000
  max_bandwidth = 100MB/s
region = us-west-2
output = json
```

The `~/.aws/credentials` file will look like the below (note, these are fake keys)
```
[hcp]
aws_access_key_id = RKIRA324234ASHDF
aws_secret_access_key = 8E8RXcAxfdadfaA9084taskrEHRm
```

## Downloading the HCP E-prime Data

To download the HCP-1200 eprime data, use the `download_eprimehcp.py` script. A number of the input values are set to default (e.g., the bucket (hcp-openaccess) and subdirectory in bucket (HCP_1200)). The rquirements are the profile that aws uses (default: hcp), the output folder where to save the eprime files (default: ./hcp-eprime), and the number of workers to parallelize over (default 6).

```bash
uv run python download_eprimehcp.py --profile hcp --output ./hcp-eprime --workers 6
```

This script will:

- Downloads E-Prime data files from the HCP (Human Connectome Project) S3 bucket
- Searches for TAB.txt files containing "eprime" in the file path for each subject in the HCP_1200 dataset
- Uses parallel downloading (with configurable number of worker threads) to efficiently download multiple files simultaneously across all of the subjects (1000+), tasks (7) and runs (2).
- Maintains the original directory structure when saving files locally

## Script converting HCP E-Prime (.txt) to Events (.csv)

This script processes HC) E-Prime data files and converts them into BIDS-compatible event files. It handles multiple task types (EMOTION, WM, GAMBLING, etc.) and organizes the output by subject, session and task.

### What the Script Does

The script performs the following operations:

1. Reads E-Prime tab-delimited files containing raw task data
2. Processes the data based on task type using task-specific preprocessing functions
3. Transforms wide-format E-Prime data into long-format BIDS-compatible event files
4. Calculates onset times, durations, and other trial-specific information
5. Organizes the output in a BIDS-compliant directory structure
6. Handles both Left-to-Right (LR) and Right-to-Left (RL) acquisition directions (which relate to runs in HCP)

For each task (such as the Working Memory task documented in the example), the preprocessing functions:
- Label trial blocks based on procedure markers
- Calculate precise onset times and durations based on the E-Prime timing information (adjusted for trigger times)
- Extract trial types, stimulus information and participant responses
- Convert timing information from milliseconds to seconds (note, response times remains in miliseconds)
- Format the data according to BIDS specifications

### Running the Script

To run the script, use the following command:

```bash
uv run python preprocess_hcp_eprime.py --input /home/user/data/hcp_eprime/HCP_1200 --output /home/user/data/hcp_events
```

- `--input` (required): Path to the folder containing HCP E-Prime files
- `--output` (required): Path where processed event files will be saved


### Output Structure

The script generates files with the following naming convention:
```
<output_dir>/sub-<subject_id>/ses-3T/func/sub-<subject_id>_ses-3T_task-<task_name>_dir-<LR/RL>_<run_num>_events.tsv
```

For example:
```
/home/user/data/hcp_events/sub-100307/ses-3T/func/sub-100307_ses-3T_task-wm_dir-LR_run2_events.tsv
```

### Supported Tasks

The script processes data for these HCP tasks by default:
- EMOTION
- MOTOR
- RELATIONAL
- SOCIAL
- WM (Working Memory)
- GAMBLING
- LANGUAGE
The names are UPPERCASE in the HCP E-PRIME input naming convesion. The task names are coverted to lowercase as part of the final file names.

## Context within E-Prime Files

The E-Prime data contains values that help us understand the structure of experimental trials, including:

- Order and sequence of different trial types
- Trial- and Block-level information
- Onset times
- Durations
- Response times

For initial blocks, timing information from E-Prime is included in parentheses to help validate the sequence of events.

These are expanded on Below

### Language Task
#### Labels
- **TaskName:** 'Story', 'Math', blank
- **Procedure[Block] Includes:**
  - "StoryProc" → Story
  - "MathProc" → Math
  - "PresentChangeProc" → When block changes from story to math, vice versa
  - "DummyProc" → Extra
- **TaskList.Sample / TaskList.Cycle / Running[Block]:** Trial array, task-related (2, 1-N, TaskList) or not (blank, blank, FinalLoop)
- **Procedure[Trial]:** 'StoryTrialProc', 'PresentMath', Blank
- **CurrentMathLevel[Trial]:** Range of math level (difficulty?)
- **CurrentStory[Trial]**

#### Timings
- **GetReady.OffSetTime:** Scanner offset, starting task (60227)
- **Story:**
  - **PresentStoryFile.OnsetTime:** Story file start (60664)
  - **PresentStoryFile.FinishTime:** End time (79311)
  - **Wait500.OnsetTime[Trial]:** Window between story and question, 500ms break (79316)
  - **Wait500.FinishTime[Trial]:** (79710)
  - **ThatWasAbout.OnsetTime:** Question for story (79836)
  - **ThatWasAbout.FinishTime:** Question offset (80997)
  - **PresentStoryOption1.OnsetTime:** Response (81182)
  - **PresentStoryOption1.FinishTime:** Response (81861)
  - **PresentStoryOption1.RTTime:** Response time (85255)
  - **PresentStoryOption1.RT:** Response time (ms) (4073)
  - **PresentStoryOption1.RESP:** Button press (2/3, index/middle?)
  - **OrAudio.OnsetTime:** Audio label (81968) *[what is this? not documented in paper]*
  - **OrAudio.FinishTime:** Audio end (82582) *[what is this? not documented in paper]*
  - **OrAudio.RTTime:** (85255) *[what is this? not documented in paper]*
  - **OrAudio.RT:** (3287) *[what is this? not documented in paper]*
  - **PresentStoryOption2.OnsetTime:** Response (82688)
  - **PresentStoryOption2.FinishTime:** Response (83507)
  - **PresentStoryOption2.RTTime:** Response time (85255)
  - **PresentStoryOption2.RT:** Response time (ms) (2567)
  - **PresentStoryOption2.RESP:** Button press (2/3, index/middle?)
  - **ResponsePeriod.OnsetTime:** (83541)
  - **ResponsePeriod.FinishTime:** (86506)
  - **ResponsePeriod.RTTime:** (85255)
  - **ResponsePeriod.RT:** (1714)
  - **ResponsePeriod.RESP:**
  - **ResponsePeriod.ACC:** 0/1 (0 corr, 1 incorr)
  - **FilteredTrialStats.RTTIME:** Same as ResponsePeriod.RTTime (85255)
  - **FilteredTrialStats.RTFromFirstOption:** 4073
- **Change block:**
  - **ExperimenterWindow.OnsetTime[Block]:** Block change start (86606)
  - **PresentBlockChange.OnsetTime:** (86726)
  - **PresentBlockChange.FinishTime:** (87448)
  - **Wait500.OnsetTime[Block]:** (87459)
  - **Wait500.FinishTime[Block]:** (87847)
- **Math:**
  - **PresentMathFile.OnsetTime:** Start Math Problem (88139)
  - **PresentMathFile.FinishTime:** (93960)
  - **PresentMathOptions.OnsetTime:** (94163)
  - **PresentMathOptions.FinishTime:** (97495)
  - **PresentMathOptions.RTTime:** (96461)
  - **PresentMathOptions.RT:** (2298)
  - **PresentMathOptions.RESP:**

#### Response Info
- **CurrentMathLevel[Trial]:** Difficulty / type
- **FilteredTrialStats.ACC:** 1 correct, 0 incorrect
- **FilteredTrialStats.RESP:** 2/3
- **OverallAcc[Trial]:** Accuracy across trials
- **CorrectResponse:** Correct response expected
- **Option1:**
- **Option2:**

### Motor Task
#### Labels
- **Procedure[Block]:** CountDownList or MOTORList.
  - Countdown is the wait period & motor is the task
  - CountDownSlide.OnsetTime: Start of slide (adjust OnsetTime minus CountDownSlide.OnsetDelay for first slide)
- **BlockType:** Left Hand, Right Hand, Left Foot, Right Foot, Tongue, Fixation

#### Timing Columns
- **LeftHandCue.OnsetTime:** Start Left Hand Cue
- **RightFootCue.OnsetTime:** Start Right Foot Cue
- **Fixdot.OnsetTime:** Onset time of fixation block
- **TongueCue.OnsetTime:** Onset time of Tongue Cue
- **LeftFootCue.OnsetTime:** Start of Left Foot cue
- **RightHandCue.OnsetTime:** Start of Right Foot Cue

### Social Task
#### Labels
- **Procedure:**
  - CountDownPROC
  - SOCIALrunPROC
  - FixationBlockPROC
- **Type:**
  - Mental → Mental condition
  - ? → Fixation
  - Random → Random condition

#### Timings
- **MovieSlide.OnsetTime:** Start of movie slide (46164)
- **ResponseSlide.OnsetTime:** Start of response window (65929)
- **FixationBlock.OnsetTime:** Start of fixation block (68994)

### Gambling Task
#### Labels
- **Running[Block]:** ReadyList, SessionSelectionList
- **Procedure[Trial]:** Blank (Initial TR), GamblingTrialPROC (trials), FixationBlockPROC (fixation)
- **TrialType:** Reward, Punishment, Neutral
- **FeedbackNumber:** 1-9

#### Timings
- **GetReady.OnsetTime:** (14385)
- **SyncSlide.OnsetTime:** Initial TRs (4)
- **QuestionMark.OnsetTime:** (73176)
- **Feedback.OnsetTime:** (38748)
- **OneSecFixation.OnsetTime:** ITI fixation (39762)
- **FifteenSecFixation.OnsetTime:** FixationBlockPROC onset (66031)

### WM Task
#### Labels
- **Procedure[Block]:** TRSyncPROC, Cue2BackPROC, TrialsPROC, Cue0BackPROC, Fix15secPROC
- **TargetType:** Nonlure, Target, Lure
- **StimType:** Body, Face, Tools, Place
- **Block-Type:** 2-Back, 0-Back

#### Timings
- **SyncSlide.OnsetTime:** Initial TR (134532)
- **Cue2Back.OnsetTime:** Onset of 2-Back (142529)
- **Stim.OnsetTime:** Stimulus onset (145101)
- **Fix15sec.OnsetTime:** Fixation block (15000ms)

### Emotion Task
#### Labels
- **Procedure:** InitialTR, ShapePromptPROC, FacePromptPROC, TrialsPROC
- **OverallAcc:** Running accuracy (0-100)

#### Timings
- **SyncSlide.OnsetTime:** Initial TR (45455)
- **StimSlide.OnsetTime:** Start of stimulus (56451)

### Relational Task
#### Labels
- **Procedure:** InitialTR, RelationalPromptPROC, RelationalPROC, ControlPromptPROC, ControlPROC, FixationPROC
- **BlockType:** Relational, Control, [BLANK]

#### Timings
- **SyncSlide.OnsetTime:** Start of initial TR (107422)
- **RelationalPrompt.OnsetTime:** Onset (115432)
- **RelationalSlide.OnsetTime:** Start of relationship stim (117498)
- **ControlPrompt.OnsetTime:** (113971)
- **ControlSlide.OnsetTime:** (135997)
- **FixationBlock.OnsetTime:** (152576)
