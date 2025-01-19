import streamlit as st
from streamlit import session_state as ss
import random
import base64
import time as tm
from PIL import Image

st.set_page_config(page_title = "Sudoku", page_icon="./sudoku_icon.png", layout = "wide", initial_sidebar_state = "expanded")

#sctn general variables
sample_gm = "921637584674518923583492167269854371745361298138729645856273419412985736397146852"
emoji_lst = {1:'1️⃣', 2:'2️⃣', 3:'3️⃣', 4:'4️⃣', 5:'5️⃣', 6:'6️⃣', 7:'7️⃣', 8:'8️⃣', 9:'9️⃣'}
entry_emoji = "❔"
# dlvllst = {"Easy": 79, "Medium": 55, "Difficult": 65}
dlvllst = {"Easy": random.randint(45, 60), "Medium": random.randint(35, 45), "Difficult": random.randint(30, 35)}
vline = f"<hr style='margin-top: 0; margin-bottom: 0; size: 1px; border: 1px dashed; color: #2E7D32; '>"
vrules = """
              <h4 style='margin-top: 0px; margin-bottom: 0px;'>Rules:</h4>
              1: Each row must contain the numbers from 1 to 9, without duplicates.<br>
              2: Each column must contain the numbers from 1 to 9, without duplicates.<br>
              3: The digits can only occur once per 3x3 block, without duplicates.<br><br>

              <h4 style='margin-top: 0px; margin-bottom: 0px;'>Other Information:</h4>
              1: To change a number, choose from its dropdown.<br>
              2: You will be intimated once the game is solved.<br>
              3: The Scratchpad will help you to eliminate numbers from a row / column / 3x3 block.<br>
              """
jumble_options = [
  "hbd 1-2",
  "hbd 1-3",
  "hbd 2-3",
  "vbd 1-2",
  "vbd 1-3",
  "vbd 2-3",
  "row 1-2",
  "row 1-3",
  "row 2-3",
  "row 4-5",
  "row 4-6",
  "row 5-6",
  "row 7-8",
  "row 7-9",
  "row 8-9",
  "col 1-2",
  "col 1-3",
  "col 2-3",
  "col 4-5",
  "col 4-6",
  "col 5-6",
  "col 7-8",
  "col 7-9",
  "col 8-9",
]

disabled_number_code = """
                          <span style='
                            width: 50px;
                            height: 38px;
                            color: #757575;
                            display: flex;
                            background-color: #f6f6f6;
                            justify-content: center;
                            align-items: center;
                            border: 2px solid black;
                            margin: 1px;
                            font-size: 16pt;
                            border-radius: 7px; '
                          >
                      """

#sctn session variables
if "changed_grid_indices" not in ss: ss.changed_grid_indices = {}
if "balance_numbers" not in ss: ss.balance_numbers = 0
if "grid_numbers" not in ss: ss.grid_numbers = [int(x) for x in sample_gm]
if "starter_func_run_once" not in ss: ss.starter_func_run_once = False

def ColSwap(vSrc, vTgt):
  src_st = (vSrc - 1)
  tgt_st = (vTgt - 1)

  for x in range(9):
    ss.grid_numbers[src_st], ss.grid_numbers[tgt_st] = ss.grid_numbers[tgt_st], ss.grid_numbers[src_st]
    src_st = src_st + 9
    tgt_st = tgt_st + 9

def RowSwap(vSrc, vTgt):
  src_nd = (vSrc * 9)
  src_st = (src_nd - 9)
  
  tgt_nd = (vTgt * 9)
  tgt_st = (tgt_nd - 9)

  ss.grid_numbers[src_st:src_nd], ss.grid_numbers[tgt_st:tgt_nd] = ss.grid_numbers[tgt_st:tgt_nd], ss.grid_numbers[src_st:src_nd]

def BandSwap(vType, vOrientation, vSrcTgt):
  if vType == "band":
    if vOrientation == "horizontal":
      if vSrcTgt == "1-2":  # swap hband 1 & 2
        RowSwap(1, 4)   # vSrc, vTgt
        RowSwap(2, 5)   # vSrc, vTgt
        RowSwap(3, 6)   # vSrc, vTgt
      
      if vSrcTgt == "1-3":  # swap hband 1 & 3
        RowSwap(1, 7)   # vSrc, vTgt
        RowSwap(2, 8)   # vSrc, vTgt
        RowSwap(3, 9)   # vSrc, vTgt

      if vSrcTgt == "2-3":  # swap hband 2 & 3
        RowSwap(4, 7)   # vSrc, vTgt
        RowSwap(5, 8)   # vSrc, vTgt
        RowSwap(6, 9)   # vSrc, vTgt

    if vOrientation == "vertical":
      if vSrcTgt == "1-2":  # swap hband 1 & 2
        ColSwap(1, 4)   # vSrc, vTgt
        ColSwap(2, 5)   # vSrc, vTgt
        ColSwap(3, 6)   # vSrc, vTgt
      
      if vSrcTgt == "1-3":  # swap hband 1 & 3
        ColSwap(1, 7)   # vSrc, vTgt
        ColSwap(2, 8)   # vSrc, vTgt
        ColSwap(3, 9)   # vSrc, vTgt

      if vSrcTgt == "2-3":  # swap hband 2 & 3
        ColSwap(4, 7)   # vSrc, vTgt
        ColSwap(5, 8)   # vSrc, vTgt
        ColSwap(6, 9)   # vSrc, vTgt

def ShowSolvedSudokuTable():
  tblhdr = """
            <style>
              table { border-collapse: collapse; font-family: Calibri, sans-serif; }
              colgroup, tbody { border: solid medium; }
              td { border: solid thin; height: 1.4em; width: 1.4em; text-align: center; padding: 0; }
            </style>
              <table>
                <colgroup><col><col><col></colgroup>
                <colgroup><col><col><col></colgroup>
                <colgroup><col><col><col></colgroup>

                <tbody>
          """
  tblftr = """
          </tbody>
        </table>
  """

  tbdy = "<tr>"
  for i in range(len(ss.grid_numbers)):
    cell_color = "" if (i+1) in ss.given_grid_indices else "background-color:#F8BBD0; "
    tbdy = tbdy + f"<td style='{cell_color}'>" + str(ss.grid_numbers[i]) + "</td>"

    if ((i+1) / 9) == int((i+1) / 9) and i != 0: tbdy = tbdy + "</tr><tr>"

  ohtml = "<center>" + tblhdr + tbdy + tblftr + "</center>"
  with st.popover("Show Solved Sudoku Puzzle", use_container_width=True): st.html(ohtml)

def GenerateGivenList(dlvl):
  start, end, num_random_numbers = 1, 81, dlvllst[dlvl]
  random_numbers = []
  while len(random_numbers) < num_random_numbers:
    rndmno = random.randint(start, end)
    if rndmno not in random_numbers: random_numbers.append(rndmno)
  
  ss.balance_numbers = 81 - dlvllst[dlvl]

  return random_numbers

def ReadPictureFile(wch_fl):
  try:
    pxfl = f"./{wch_fl}"
    return base64.b64encode(open(pxfl, 'rb').read()).decode()

  except: return ""

def CheckBoxSelectUnselect(what_to_do): 
  wtd_val = False if what_to_do == 'clear' else True
  for i in range(1,10): ss[f"cb{i}"] = wtd_val

def CheckIfSolved():
  all_solved = []
  for k in ss.changed_grid_indices.keys(): all_solved.append(False if ss.changed_grid_indices[k] != ss.grid_numbers[k-1] else True)

@st.fragment
def ShowScratchpad():
  with st.popover("Scratchpad", use_container_width=True):
    st.markdown("✍️ Number Scratchpad:")
    
    scols1 = st.columns(5)
    for i in range(1,6): scols1[i-1].checkbox(str(i), key=f"cb{i}")
    
    scols2 = st.columns(5)
    for j in range(6,10): scols2[j-6].checkbox(str(j), key=f"cb{j}")

    sc1, sc2 = st.columns(2)
    sc1.button("Select All", key="clrbtn", on_click=CheckBoxSelectUnselect, args=('select',), use_container_width=True)
    sc2.button("Clear All", key="slbtn", on_click=CheckBoxSelectUnselect, args=('clear',), use_container_width=True)

def PopOverChanged(ptr): ss.changed_grid_indices[ptr] = ss[f"B{ptr}"]

def DisplayGame():
  # st.html(" <style> .st-emotion-cache-ocsh0s { background-color: #F8BBD0; color: black } </style> ")

  ptr = 0
  for r in range(1, 10):
    globals()['cols' + str(r)] = st.columns((3,3,3,1,3,3,3,1,3,3,3))
    for c in range(1, 12):
      if c == 4 or c == 8: globals()['cols' + str(r)][c-1].markdown("|", True)
      
      else:
        if (ptr + 1) in ss.given_grid_indices:
          globals()['cols' + str(r)][c-1].html(disabled_number_code + f'{ss.grid_numbers[ptr]}</span>')

        else:
          with globals()['cols' + str(r)][c-1].popover(str(ss.changed_grid_indices[ptr+1]), use_container_width=False): 
            st.segmented_control("Choose a number", 
                                  options=[0,1,2,3,4,5,6,7,8,9], 
                                  selection_mode='single', 
                                  key=f"B{ptr+1}",
                                  on_change=PopOverChanged, 
                                  args=(ptr+1,))
            
        ptr = ptr + 1
    
    if (r / 3) == int(r / 3) and r < 9: st.markdown(vline, True)

def StarterFunctionRunOnce():
  active_option = random.choice(jumble_options)
  jumble_cmd, jumble_st, jumble_nd = active_option[0:3], int(active_option[4]), int(active_option[6])

  if jumble_cmd == "row": RowSwap(jumble_st, jumble_nd)   # vSrc, vTgt
  if jumble_cmd == "col": ColSwap(jumble_st, jumble_nd)   # vSrc, vTgt
  if jumble_cmd == "hbd": BandSwap("band", "horizontal", f"{jumble_st}-{jumble_nd}")  # vType, vOrientation, vSrcTgt
  if jumble_cmd == "vbd": BandSwap("band", "vertical",   f"{jumble_st}-{jumble_nd}")  # vType, vOrientation, vSrcTgt


  dlvl = random.choice([x for x in dlvllst.keys()])
  # dlvl = "Easy" #WARN TBD
  if "given_grid_indices" not in ss: ss.given_grid_indices = GenerateGivenList(dlvl)

  ss.given_grid_indices.sort()

  for x in range(1,82): 
    if x not in ss.given_grid_indices: ss.changed_grid_indices[x] = '0'

  ss.starter_func_run_once = True

  # st.html(" <style> .st-emotion-cache-ocsh0s { background-color: #F8BBD0; color: black } </style> ")

def Main():
  sudoku_icon = f"""<img src="data:gif;base64,{ReadPictureFile('sudoku_sidebar_icon.png')}" width="65" height="50">"""

  if ss.starter_func_run_once == False: StarterFunctionRunOnce()
  
  main_container = st.empty()

  with main_container.container(border=True):
    try: DisplayGame()
    except: st.warning("✋ Invalid move. Please refresh screen for new game.")

  with st.sidebar:
    sc1, sc2 = st.columns((1.5,4))
    sc1.markdown(sudoku_icon, unsafe_allow_html=True)
    sc2.html("<h1 style='font-size:2.1em; margin-top:0px; margin-bottom:0px; padding-top:0px;'>Sudoku:</h1>")
    st.html("<span style='font-size: 14px; color: blue; margin-top:0px; margin-bottom:0px; padding-top:0px; '>↻ Refresh screen / page for new game...</span>")
    st.markdown(vline, True)

    with st.expander(" How to play:", expanded=False, icon=':material/psychology_alt:'): st.html(vrules)

    ShowScratchpad()
    ShowSolvedSudokuTable()
    CheckIfSolved()

    st.markdown(vline, True)

    author_dtl = "<strong>😎 Shawn Pereira: Happy Playing:<br>shawnpereira1969@gmail.com</strong>"
    st.markdown(author_dtl, unsafe_allow_html=True)

  all_solved = []
  for k, v in ss.changed_grid_indices.items(): all_solved.append(False if v != ss.grid_numbers[k-1] else True)
  if all(all_solved) and len(all_solved) > 0 and len(all_solved) == (81 - len(ss.given_grid_indices)):
    st.balloons()
    tm.sleep(2)
    main_container.markdown(f"""<img src="data:jpg;base64,{ReadPictureFile('won_pix.jpg')}" width='600' height='500' >""", unsafe_allow_html=True)

def LandingPage():
    bkgrnd_img = "./LandingPage.jpg"
    bkgrnd_img_ext = bkgrnd_img[-4:-1]
    img_code = f"""<style>
                        .stApp {{
                            background: url(data:image/{bkgrnd_img_ext};base64,{base64.b64encode(open(bkgrnd_img, 'rb').read()).decode()});
                            background-repeat: no-repeat;
                            background-attachment: fixed;
                            background-size: 100% 100%;
                        }}
                    </style>"""

    st.markdown(img_code, unsafe_allow_html=True)

    tm.sleep(2)
    ss.runpage = Main
    st.rerun()

if 'runpage' not in ss: ss.runpage = LandingPage
# if 'runpage' not in ss: ss.runpage = Main
ss.runpage()
