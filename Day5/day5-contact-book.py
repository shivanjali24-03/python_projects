
contact={}

while True:
    print("1. Add Contact")
    print("2. View Contact")
    print("3. Search Contact")
    print("4. Delete contact")
    print("5. Exit")

    choice =int(input("Enter Your Choice : "))

    match choice:
        case 1:
            #contactName = input("Enter Contact Name : ").strip().lower() 
            raw_name = input("Enter Contact Name: ")
            contactName = " ".join(raw_name.strip().split()).lower()
            contactNumber = input("Enter Contact Number ").strip()

            if contactName == "":
                print("\n Name cannot be Empty \n")
            
            elif not contactName.replace(" ", "").isalpha():
                print("Name should contain only letters and spaces")
            
            elif contactName in contact:
                print("\n Name already Present \n")

            elif contactNumber in contact.values():
                print("\n This number is already assigned to another contact! \n ")
            
            elif len(contactNumber) != 10 or not contactNumber.isdigit():
                print("\n Enter a Valid Number \n")
            else:
                contact[contactName] = contactNumber
                print("\n Contact added  Sucessfully \n")
                

        case 2:
            print("Option coming soon...")
            if not contact:
                print("\n -------------Empty Contact Book------------")

            else:
                print("\n-------------Contact List A-Z------------\n")

                for name in sorted(contact):
                    print(name.title(), " : ",contact[name])

        case 3:
            if not contact:
                print("\n -------------Contact Book is Empty --------------\n")

            else:
                raw_name = input("Enter Contact Name: ")
                search = " ".join(raw_name.strip().split()).lower()
                
                if search == "":
                    print("Enter something to search.")
                elif not search.replace(" ", "").isalpha():
                    print("Search should contain only letters and spaces.")
                else:
                    found = False
                    print("\n---- Search Results ----\n")

                    for name, number in contact.items():
                        if search in name:  # partial match
                            print(name.title(), ":", number)
                            found = True

                    if not found:
                        print("No matching contacts found.")
        case 4:
            if not contact:
                print("\n -------------Contact Book is Empty --------------\n")

            else:
                raw_name = input("Enter Contact Name to delete: ")
                search = " ".join(raw_name.strip().split()).lower()
                
                if search == "":
                    print("Enter something to delete.")
                elif not search.replace(" ", "").isalpha():
                    print("Name should contain only letters and spaces.")
                else:
                    matches = []
                    for name in contact:
                        if search in name:
                            matches.append(name)

                    if not matches:
                        print("No Matching contact found to delete")

                    elif len(matches) == 1:
                        name_to_delete = matches[0]
                        del contact[name_to_delete]
                        print(f"Deleted: {name_to_delete.title()}")

                    else:
                        print("\n ------Multiple Matches Found-------")

                        for i, name in enumerate(matches, start=1):
                            print(f"{i}. {name.title()} : {contact[name]}")

                        try:
                            idx = int(input("Enter number to delete: "))
                            if 1 <= idx <= len(matches):
                                name_to_delete = matches[idx - 1]
                                del contact[name_to_delete]
                                print(f"Deleted: {name_to_delete.title()}")
                            else:
                                print("\nInvalid selection\n")

                        except ValueError:
                            print("Please enter a valid Number")

        case 5:
            print("Exiting...")
            break
        case _:
            print("Invalid choice. Try again.")
        
