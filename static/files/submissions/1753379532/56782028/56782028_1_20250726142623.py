import turtle
import math

scr = turtle.Screen()
pen = turtle.Turtle()
pen.speed("fastest")

def draw_sinos(mag, phase, omega, graph_thickness, graph_color, axes_color, startAng, numRev):
    def deg2rad(angDeg):
        return (math.pi/180) * angDeg
    
    
    # function to calculate y given an x [y = sin(wx + p)]
    def f_x(x, mag, phase, omega):
        return mag * math.sin(deg2rad(omega*x + phase))
    
    #Function to display plotted point labels
    def display_pt(x,y):
        pen.penup()
        pen.goto(x-1, y)
        pen.write(f"({x:.0f},{y:.1f})", align="right", font=("Arial, 10"))
        pen.goto(x, -mag - 0.5*line_ofst)
        pen.write(x, align="left",font=("Arial”, 10))
        pen.goto(x,y)
        pen.pendown()
        
    line_ofst = 2 # offsets from graph and axes line
    xAxis_len = (360 - 0)*numRev + 2*line_ofst
    yAxis_len = mag + line_ofst
    
    scr.bgcolor("#000010")
    scr.setworldcoordinates(startAng - line_ofst - 1, 
                            -mag - 0.5*line_ofst - 1, 
                            xAxis_len - line_ofst + 1, 
                            mag + 0.5*line_ofst + 1
                        )
    
    
    # draw axes
    pen.color(axes_color)
    pen.pensize(1)
    
    pen.up()
    pen.goto(-line_ofst, 0)
    pen.down()
    pen.goto(xAxis_len, 0)
    pen.write("x",align='left',font=("Arial”, 12))
    
    pen.up()
    pen.goto(0, -mag - 0.5*line_ofst)
    pen.down()
    pen.goto(0, yAxis_len)
    pen.write("y",align='left',font=("Arial”, 12))
    
    
    # draw the graph
    pen.color(graph_color)
    pen.pensize(graph_thickness)  # make graph bolder
    
    x = 0
    
    pen.up()
    pen.goto(x, f_x(x, mag, phase, omega))
    pen.down()
    
    stop_x = 360 * numRev
    while x <= stop_x:
        y = f_x(x, mag, phase, omega)
        pen.goto(x, y)
        
        if x % 90 == 0:
            display_pt(x,y)
        elif x == 180:
            display_pt(x,y)
            pen.penup()
            pen.goto(x, y + mag)
            pen.write(f"y = {mag:.0f}sin({omega:.0f}x+{phase:.0f})",align="left",font=("Arial", 10))
            pen.goto(x,y)
            pen.pendown()
        
        x += 0.5
    
mag = float(input("Enter the amplitude of the sinusoid: "))
phase = float(input("Enter the phase of the sinusoid: "))
omega = float(input("Enter the frequency of the sinusoid: "))
axes_color = input("Enter the axes color: ")
graph_color = input("Enter the graph color: ")
graph_thickness = int(input("Enter the thickness of the graph: "))
startAng = int(input("Enter the start angle of the sinusoid: "))
numRev = int(input("Enter the number of revolutions of the sinusoid: "))

draw_sinos(mag, phase, omega, graph_thickness, graph_color, axes_color, startAng, numRev)

turtle.done()
