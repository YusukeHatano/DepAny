import socket
import time

HOST = "192.168.56.1"
PORT = 30002

# karioki
DEPTH = 0.10
def deg2rad(degvec):
    rad = np.deg2rad(degvec)
    #difine degrees  from bottom to upper
    radvec = [rad[0],rad[1],rad[2],rad[3],rad[4],rad[5]]
    return radvec

def toBytes(message):
     
     return bytes(message.encode())


class NegiUR3:
    def __init__(self):
        #basic position
        self.home = deg2rad([0, -90, 0, -90, 0, 0])
        #negi home position
        self.home_2 = deg2rad([315.22, -90, 0, -90, 0, 0])
         #tool chatching potiion
        self.under_tool_1 = deg2rad([305.91, -152.04 ,-77.49, -128.92, 125.89, -176.93])
        self.upper_tool_1 = deg2rad([306.34, -129.59, -71.00, -159.36 ,126.03, -181.72])
        self.Waypoint_1 = deg2rad([247.55, -115.53, -82.47, -159.43, 135.42, -92.09])
        self.Waypoint_2 = deg2rad([248.45, -75.42, -68.73, -125.74, 90.86, -7.80])
        self.safe_pose_1 = deg2rad([217.02, -77.08, -66.82, -126.64, 90.71, -39.23])
        #above negi utsuwa 
        self.upon_negi = deg2rad([213.53, -109.75, -38.11, -122.19, 89.47, 33.95])
         #table
        self.upon_table = deg2rad([23.07, -82.85, -42.55, -130.17, 89.81, -4.71])
        #1st dish
        self.utsuwa_1 = deg2rad([24.33,-126.43, -48.43, -73.81, 73.74, 9.68])
        #2nd dish
        self.utsuwa_2 = deg2rad([24.37, -113.29, -55.72, -96.30, 85.10, 8.63])
        self.safe_pose_2 = deg2rad([10.16, -95.85, -51.40, -138.83, 130.55, 8.36])
        self.upper_tool_2 = deg2rad([-54.12, -130.43, -73.71, -153.34, 125.85, -179.02])
        self.under_tool_2 = deg2rad([-54.06, -152.85, -77.61, -127.15, 126.00, -179.02])

    def def_move(self):

        self.tool_catch = (
            "def myProg():"+"\n"
            +f"movej({self.home_2},a=9.0,v=9.0)"+"\n"
            +f"movej({self.under_tool_1},a=9.0,v=9.0)"+"\n"
            +f"movel({self.upper_tool_1},a=0.1,v=0.25)"+"\n"
            +f"movej({self.Waypoint_1},a=9.0,v=9.0)"+"\n"
            +f"movej({self.Waypoint_2},a=9.0,v=9.0)"+"\n"
            +f"movej({self.safe_pose_1},a=5.0,v=3.0)"+"\n"
            +"end"+"\n")
        
        self.negi_catch = (
            "def myProg():"+"\n"
            +"set_tool_digital_out(0,False)" + "\n"
            +f"movej({self.upon_negi},a=5.0,v=5.0)"+"\n"
            +"begin_pos = get_actual_tcp_pose()" +"\n"
            +f"pos_end = pose_add(begin_pos, p[0.0, 0.0, {DEPTH}, 0.0, 0.0, 0.0])" +"\n"
            +"movel(pos_end , a=0.5, v=0.75)" + "\n"
            +"sleep(1.)"+"\n"
            +"set_tool_digital_out(0,True)" + "\n"
            +"sleep(1.)"+"\n"
            +f"movel({self.upon_negi},a=0.5,v=0.75)"+"\n"
            +f"movej({self.safe_pose_1},a=1.0,v=3.0)"+"\n"
            +"end"+"\n")     
        self.move_go = (
            "def myProg():"+"\n"
            +f"movej({self.upon_table},a=1.5,v=2.0)"+"\n" 
            +"end"+"\n")
        
        self.moritsuke = (
            "def myProg():"+"\n"
            +f"movej({self.utsuwa_2},a=1.5,v=1.5)"+"\n"
            +"sleep(1.)"+"\n"
            +"set_tool_digital_out(0,False)" + "\n"
            +"sleep(1.)"+"\n"
            +f"movej({self.upon_table},a=4.0,v=4.0)"+"\n"
            +"set_tool_digital_out(0,True)" + "\n"
            +f"movej({self.safe_pose_2},a=6.0,v=6.0)"+"\n"
            +"end"+"\n")
        
        self.move_back = (
            "def myProg():"+"\n"

            )
        
        self.tool_release = (
            "def myProg():"+"\n"
            +f"movej({self.under_tool_2})"+"\n"
            +f"movej({self.upper_tool_2})"
            +f"movej({self.Waypoint_1},a=9.0,v=9.0)"+"\n"
            +f"movej({self.Waypoint_2},a=9.0,v=9.0)"+"\n"
            +f"movej({self.safe_pose_1},a=5.0,v=3.0)"+"\n"
            +"end"+"\n")



