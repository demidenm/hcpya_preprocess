


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