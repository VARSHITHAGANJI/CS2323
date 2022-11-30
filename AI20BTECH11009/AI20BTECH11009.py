
# AUTHOR: AI20BTECH11009 (GANJI VARSHITHA)

#Dictionary for mapping formats with opcode
opcode = { 51: 'R', 19: 'I', 3: 'I_L', 35: 'S', 99:'B',111: 'J', 103:'I_J',55:'U' }
#Dictionary for mapping R- format instructions based on 2 funct 7 values : 0: R0, 32: R1
R0 = { 0: 'add', 4: 'xor',6:'or',7:'and',1:'sll',5:'srl' }
R1 = {0: 'sub',5: 'sra'}
funct7 = {0: R0, 32: R1} #funct7 for R format
I_f3 = {0: 'addi',4:'xori',6:'ori',7:'andi',1:'slli'} #funct3 for I type arithmetic instructions
I_L1 = {0:'lb',1:'lh',2:'lw',3:'ld',4:'lbu',5:'lhu',6:'lwu'} #funct3 for I type load instructions
S_f3 = {0:'sb',1:'sh',2:'sw',3:'sd'} #funct3 for S type store instructions
B_f3 = {0:'beq',1:'bne',4:'blt',5:'bge',6:'bltu',7:'bgeu'} # funct3 for B type branch instructions


#Subroutine for calculating number specified by number of bits and starting position of original number
def bits(num, start, num_bits):  
  return ( ((1 << num_bits) - 1)  &  (num >> (start-1) ) )




class instr_str():
  def __init__(self,data,offset):
    ''' Constructor class for disassembly code for each machine instruction '''
    self.data = data #string of instruction
    self.offset = offset #offset of instruction: mostly 0 and used for branch instruction

#In all formats, extract rd,rs1,rs2 depending on the format

def R(code):
  f7 = bits(code,26,7) #Get f7
  rd = "x"+str(bits(code,8,5))+", "
  rs1 = "x"+str(bits(code,16,5))+", "
  rs2 = "x"+str(bits(code,21,5))
  f3 = bits(code,13,3) #Get f3
  # funct7[f7][f3] maps which set of f3 to go and which instruction corresponds to that f3
  fn = funct7[f7][f3] +" " + rd+rs1+rs2
  return fn,0

def I(code):
  rd = "x"+str(bits(code,8,5))+", "
  rs1 = "x"+str(bits(code,16,5))+", "
  f3 = bits(code,13,3)
  fn = ""
  imm = bits(code,21,11) + bits(code,32,1)*(-2**11)
  # Signed integer hence last bit is multiplied by -2*11
  #Special case of srli and srai as both have funct3 = 5, but first 7 bits of immediate field are reserved for
  # distinguishing both
  if(f3 == 5): 
    imm_1 = bits(code,21,12)
    imm_6 = bits(imm_1,6,6)
    imm_5 = bits(imm_1,1,5) #last 5 bits as the range is 0 - 31
    
    if(imm_6==0):
      fn += "srli " + rd+rs1+ str(imm_5)
    elif(imm_6==32):
      
      fn += "srai " + rd+rs1+ str(imm_5)
      
  else:
    fn += I_f3[f3] +" " + rd+ rs1+ str(imm) 
    
  return fn,0

def I_L(code):
  rd = "x"+str(bits(code,8,5))+", "
  rs1 = "x"+str(bits(code,16,5))
  f3 = bits(code,13,3)
  fn = ""
  imm = bits(code,21,11) + bits(code,32,1)*(-2**11)
     
  
  fn += I_L1[f3] +" " + rd+  str(imm) +"("+rs1+")"
    
  return fn,0

def S(code):
  rs1 = "x"+str(bits(code,16,5))
  rs2 = "x"+str(bits(code,21,5))+", "
  fn=""
  
  imm_5 = bits(code,8,5)
  imm_6 = bits(code,26,6)<<5
  imm = imm_5 + imm_6 + bits(code,32,1)*(-2**11)
  f3 = bits(code,13,3)
  fn += S_f3[f3] + " " + rs2 + str(imm) +"("+rs1+")"
  return fn,0

def B(code):
  rs1 = "x"+str(bits(code,16,5))+", "
  rs2 = "x"+str(bits(code,21,5)) + ", "
  # instead of left shifting whole 12 bits, extracted few and left shifted 
  imm_3 = bits(code,9,3)*2
  
  imm_4 = bits(code,12,1)*16
  
  imm_6 = bits(code,26,6)<<5
  
  imm_1 = bits(code,8,1)<<11
  
  imm_2 = bits(code,32,1)*(-2**12)
  
  imm = imm_3+imm_4+imm_6 + imm_1 +imm_2
  f3 = bits(code,13,3)
  fn=""
  fn+= B_f3[f3] + " " + rs1+rs2 + str(imm)
  return fn, imm + 1 #returning offset

def U(code):
  rd = "x"+str(bits(code,8,5))+", "
  imm = bits(code,13,20)
  imm_h = hex(imm) # getting first 5 hex digits of machine code by converting last 20 bits to 5 hex digits
  fn = 'lui' + " " + rd+ imm_h
  return fn,0

def J(code):
  rd = "x"+str(bits(code,8,5))+", "
  # instead of left shifting whole 20 bits, extracted few and left shifted 
  imm_9 = bits(code,22,9)*2
  imm_10 = bits(code,31,1)*(2**10)
  imm_11 = bits(code,21,1)*(2**11)
  imm_8 = bits(code,13,8)<<12
  imm_20 = bits(code,32,1)*(-2**20) #signed bit msb multiplied by -2**20
  imm = imm_9 + imm_10 + imm_11 + imm_8 + imm_20
  
  fn = 'jal ' + " " + rd + str(imm)
  return fn,imm+1

def I_J(code):
  #jalr instruction
  rd = "x"+str(bits(code,8,5))+" "
  rs1 = "x"+str(bits(code,16,5)) + " "
  f3 = bits(code,13,3)
  #same as immediate field of I type
  imm = bits(code,21,11) + bits(code,32,1)*(-2**11)
  
  
      

  fn = 'jalr' +" " + rd+  rs1 + str(imm)
    
  return fn,0



def parse(line):
  p = str(line.split('\n')[0]) 
  
  m_code = int(p,16) # m_code in decimal

  op = bits(m_code,1,7) #extracting opcode

  data = eval(opcode[op])(m_code) #calling function using eval as the value of each key is a function name

  i = instr_str(data[0],data[1]) # instance of instr_str class: i object

  return i

offsets = {}


with open('input.txt', 'r') as file_in, open("output.txt", "w") as outfile:
  lines = file_in.readlines()
  #generating branch names
  branches = [ "L"+str(i) for i in range(len(lines))]
  i = 0
  for line in lines:
    
    words = line.split()
   
    if(len(words)!=0):
      instr_string = parse(line.split()[0:8][0])
      if(instr_string.offset!= 0):
        offsets[i] = instr_string.offset-1
      i+=1
      outfile.write(instr_string.data + "\n")


with open('output.txt',"r") as outfile:
  out = outfile.readlines()



for key in offsets.keys():
  data = out[key]
  branch_label = " "
  
  branch_str = data.split(',')[-1]
  if(offsets[key]==0):
    branch_label = branches.pop(0)
    new_str = branch_label + " : "
    for i in range(len(data.split(','))-1):
        new_str += data.split(',')[i] + ", " 
    new_str +=  branch_label + "\n"
    out[key] = new_str
  else:
    line = offsets[key]//4 # get number of lines by dividing offset by 4 : branch is at line num: (key+line)
    b_line = out[key+line]
    if(b_line[0]=='L'): #if the line is already having a label: get the label
        branch_label = b_line.split(':')[0]
    else:
        branch_label = branches.pop(0)
    new_str = ""
    for i in range(len(data.split(','))-1):
        new_str += data.split(',')[i] + ", " 
    new_str +=  branch_label + "\n"
    out[key] = new_str
    out[key+line] = branch_label + ": " + b_line
 

with open('output.txt',"w") as outfile:
  outfile.writelines(out)
  
