# tasks/__init__.py - Central import for all task modules

from .storymode_tasks import StoryMode_Tasks
from .restarting_tasks import Restarting_Tasks
from .shared_tasks import Shared_Tasks
from .switcher_tasks import Switcher_Tasks
from .guild_tasks import GUILD_TUTORIAL_TASKS, Guild_Rejoin
from .sell_characters_tasks import Sell_Characters
from .sell_accsesurry_tasks import Sell_Accessury
from .hard_story import HardStory_Tasks
from .side_story import SideStory
from .sub_stories import SubStories
from .sub_stories_check import SubStories_check
from .character_slots_purchase import Character_Slots_Purchase
from .exchange_gold_characters import Exchange_Gold_Characters
from .recive_giftbox import Recive_GiftBox
from .recive_giftbox_check import Recive_Giftbox_Check
from .recive_giftbox_orbs import Recive_Giftbox_Orbs
from .recive_giftbox_orbs_check import Recive_Giftbox_Orbs_Check
from .skip_kon_bonaza import Skip_Kon_Bonaza
from .Kon_Bonaza_1Match_Tasks import Kon_Bonaza_1Match_Tasks
from .skip_yukio_event_tasks import Skip_Yukio_Event_Tasks
from .sort_characters_lowest_level_tasks import Sort_Characters_Lowest_Level_Tasks
from .sort_filter_ascension_tasks import Sort_Filter_Ascension_Tasks
from .sort_multi_select_garbage_first_tasks import Sort_Multi_Select_Garbage_First_Tasks
from .upgrade_characters_level_tasks import Upgrade_Characters_Level
from .upgrade_characters_back_to_edit import Upgrade_Characters_Back_To_Edit
from .main_screenshot_tasks import Main_Screenshot_Tasks
from .extract_orb_counts import Extract_Orb_Counts_Tasks
from .extract_account_id import Extract_Account_ID_Tasks
from .login1_prepare_for_link_tasks import Login1_Prepare_For_Link_Tasks
from .login2_klab_login_tasks import Login2_Klab_Login_Tasks
from .login3_wait_for_2fa import Login3_Wait_For_2FA_Tasks
from .login4_Confirm_Link import Login4_Confirm_Link_Tasks
from .endgame_tasks import Endgame_Tasks
# Reroll tasks
from .reroll_earse_gamedata_1 import reroll_earse_gamedata_tasks
from .reroll_tutorial_firstMatch_2 import reroll_tutorial_firstmatch_tasks
from .reroll_tutorial_CharacterChoose_3 import reroll_tutorial_characterchoose_tasks
from .reroll_tutorial_secondMatch_4 import reroll_tutorial_secondmatch_tasks
from .reroll_tutorial_ReplaceIchigoWithFiveStar_5 import reroll_replaceichigowithfivestar_tasks

__all__ = [
    'StoryMode_Tasks',
    'Restarting_Tasks',
    'Shared_Tasks',
    'Switcher_Tasks',
    'GUILD_TUTORIAL_TASKS',
    'Guild_Rejoin',
    'Sell_Characters',
    'Sell_Accessury',
    'HardStory_Tasks',
    'SideStory',
    'SubStories',
    'SubStories_check',
    'Character_Slots_Purchase',
    'Exchange_Gold_Characters',
    'Recive_GiftBox',
    'Recive_Giftbox_Check',
    'Recive_Giftbox_Orbs',
    'Recive_Giftbox_Orbs_Check',
    'Skip_Kon_Bonaza',
    'Kon_Bonaza_1Match_Tasks',
    'Skip_Yukio_Event_Tasks',
    'Sort_Characters_Lowest_Level_Tasks',
    'Sort_Filter_Ascension_Tasks',
    'Sort_Multi_Select_Garbage_First_Tasks',
    'Upgrade_Characters_Level',
    'Upgrade_Characters_Back_To_Edit',
    'Main_Screenshot_Tasks',
    'Extract_Orb_Counts_Tasks',
    'Extract_Account_ID_Tasks',
    'Login1_Prepare_For_Link_Tasks',
    'Login2_Klab_Login_Tasks',
    'Login3_Wait_For_2FA_Tasks',
    'Login4_Confirm_Link_Tasks',
    'Endgame_Tasks',
    # Reroll tasks
    'reroll_earse_gamedata_tasks',
    'reroll_tutorial_firstmatch_tasks',
    'reroll_tutorial_characterchoose_tasks',
    'reroll_tutorial_secondmatch_tasks',
    'reroll_replaceichigowithfivestar_tasks'
]