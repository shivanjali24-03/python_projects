#Grade Calculator

marks = int( input("ENter marks (0-100) : "))

if marks <= 0  and  marks >= 100:
    print("Invalid Marks")
elif marks >=90:
    print("Grade A : ", marks)
elif marks >= 80:
    print("Grade B : ",marks)
elif marks >= 70:
    print("Grade C : ", marks)
else:
    print("Fail : ",marks)
