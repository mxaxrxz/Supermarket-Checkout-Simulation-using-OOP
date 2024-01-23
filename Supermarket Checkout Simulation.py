from datetime import datetime
import random
import time

max_regular = 5
max_self_service = 15

#  Constants for checkout time
cashier_fixed_time = 4
self_service_fixed_time = 6

# Get the current date and time
current_time = datetime.now()  # Use datetime.now() directly
# Format the timestamp as a string
timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
# Display the timestamp at the start of the simulation
print(f"Simulation started at {timestamp_str}")


class Lane:
    """
        Represents 6 lanes in a store.

        Attributes:
        - lane_type: Type of the lane (Regular or Self Service)
        - customers: List of Customer objects currently in the lane
        - max_capacity: Maximum number of customers the lane can accommodate
        - timestamp: Timestamp representing when the lane was created
        - status: Current status of the lane (Open or Closed)

        Methods:
        - __init__(self, lane_type, max_capacity, status="Closed"): Initializes a Lane object with the provided attributes.
        - add_customer(self, customer): Adds a customer to the lane if it's open and has space.
        - can_accept_customer(self, customer): Checks if the lane can accept the given customer.
        - remove_customer(self, customer): Removes a customer from the lane if checkout conditions are met.
        """

    def __init__(self, lane_type, max_capacity, status="Closed"):
        """
        Represents a lane in the store.

        Parameters:
        - lane_type: Type of the lane (Regular or Self Service)
        - max_capacity: Maximum number of customers the lane can accommodate
        - status: Current status of the lane (Open or Closed)
        """
        self.lane_type = lane_type
        self.customers = []
        self.max_capacity = max_capacity
        self.timestamp = datetime.now()
        self.status = status

    def add_customer(self, customer):
        """
        Adds a customer to the lane if the lane is open and has space.

        Parameters:
        - customer: Customer object to be added to the lane

        Returns:
        - True if the customer is added, False otherwise
        """
        if self.can_accept_customer(customer):
            self.customers.append(customer)
            print(f"C{customer.identifier} joined {self.lane_type}.")
            return True
        else:
            return False

    def can_accept_customer(self, customer):
        """
        Checks if the lane can accept the given customer.

        Parameters:
        - customer: Customer object

        Returns:
        - True if the lane can accept the customer, False otherwise
        """
        return len(self.customers) < self.max_capacity and self.status == "Open"

    def remove_customer(self, customer):
        """
        Removes a customer from the lane if checkout conditions are met.

        Parameters:
        - customer: Customer object to be removed from the lane
        """
        checkout_time = customer.checkout_time()  # Use the customer's checkout_time method
        elapsed_time = datetime.now() - customer.join_timestamp
        if elapsed_time.total_seconds() >= checkout_time:
            self.customers.remove(customer)
            print(f"C{customer.identifier} has completed checkout and left {self.lane_type}.")


class Status:
    """
        Represents the status of multiple lanes in the store.

        Attributes:
        - lanes: List of Lane objects

        Methods:
        - __init__(self, lanes): Initializes a Status object with the provided list of Lane objects.
        - open_next_lane(current_lane): Opens the next regular lane if conditions are met.
        - set_statuses(lane): Sets the status of a lane based on the number of customers.
        - display_status(*lanes): Displays the status of multiple lanes.
        """

    def __init__(self, lanes):
        """
        Represents the status of multiple lanes in the store.

        Parameters:
        - lanes: List of Lane objects
        """
        self.lanes = lanes

    @staticmethod
    def open_next_lane(current_lane):
        """
        Opens the next regular lane if conditions are met.

        Parameters:
        - current_lane: Type of the current lane
        """

        lane_number = int(current_lane.split()[-1])
        next_lane_type = f"Regular {lane_number + 1}"
        for lane in lanes:
            if lane.lane_type == next_lane_type and len(lane.customers) <= lane.max_capacity:
                lane.status = "Open"

    @staticmethod
    def set_statuses(lane):
        """
             Sets the status of a lane based on the number of customers.

             Parameters:
             - lane: Lane object
             """
        if len(lane.customers) == lane.max_capacity:
            Status.open_next_lane(lane.lane_type)
        elif len(lane.customers) == 0:
            lane.status = "Closed"
        else:
            lane.status = "Open"

    @staticmethod
    def display_status(*lanes):
        """
        Displays the status of multiple lanes.

        Parameters:
        - lanes: List of Lane objects
        """
        for lane in lanes:
            status_message = f"{lane.lane_type} --> {lane.status}"
            if lane.customers:
                status_message += f" ({len(lane.customers)} customers): "
                status_message += ", ".join(
                    [f"C{customer.identifier} ({customer.items} items)" for customer in lane.customers])
            print(status_message)
        print()


class Customer:
    latest_id = 0  # Class variable to track the latest customer identifier

    def __init__(self):
        Customer.latest_id += 1
        self.identifier = Customer.latest_id
        self.items = random.randint(1, 30)
        self.join_timestamp = datetime.now()

    def checkout_time(self):
        if self.items >= 10:
            return self.items * cashier_fixed_time
        else:
            return self.items * self_service_fixed_time


def assign_lane(customer, lanes, status_instance):
    """
    Assigns a lane to a customer based on the number of items in the basket and the availability of lanes.

    Parameters:
    - customer: Customer object
    - lanes: List of Lane objects
    - status_instance: Status object to manipulate the status of lanes

    Returns:
    - Lane type (either "Self Service" or a "Regular" lane type) where the customer is assigned.
    """
    if customer.items < 10:
        return "Self Service"
    else:
        # Iterate through Regular lanes to find an available lane with space for the customer
        for lane in lanes:
            if lane.lane_type.startswith("Regular") and len(
                    lane.customers) < lane.max_capacity and customer not in lane.customers:
                return lane.lane_type

        # If all regular lanes are full, open the next regular lane if possible
        for lane in lanes:
            if lane.lane_type.startswith("Regular") and len(lane.customers) == lane.max_capacity:
                status_instance.open_next_lane(lane.lane_type)
                return lane.lane_type  # Assign the customer to the newly opened lane

    # If all regular lanes are full and opening a new lane is not possible, return "Self Service" as a fallback
    return "Self Service"


def add_customer_to_lane(customer, lane_type, lanes, status_instance):
    """
    Adds a customer to the specified lane and updates the status of the lane.

    Parameters:
    - customer: Customer object to be added to the lane
    - lane_type: Type of the lane to which the customer should be added
    - lanes: List of Lane objects
    - status_instance: Status object to manipulate the status of lanes
    """
    for lane in lanes:
        if lane.lane_type == lane_type:
            if lane.add_customer(customer):
                status_instance.set_statuses(lane)
            break


class Simulation:
    """
    A class representing a simulation of customer behavior in a store.

    Attributes:
    - lanes: List of Lane objects representing different checkout lanes in the store.
    - status_instance: An instance of the Status class for managing and displaying the status of lanes.

    Methods:
    - __init__(self, lanes, status_instance): Constructor method for initializing the Simulation object.
    - simulate_interval(self, interval_seconds): Simulates a fixed time interval of customer behavior in the store.
    - end_simulation(self): Asks the user if they want to end the simulation.
    - run_simulation(self): Runs the main simulation loop until the user decides to end it.
    """

    def __init__(self, lanes, status_instance):
        """
        Initialize the Simulation object with lanes and a status instance.

        Parameters:
        - lanes: List of Lane objects representing different checkout lanes.
        - status_instance: An instance of the Status class.
        """
        self.lanes = lanes
        self.status_instance = status_instance

    def simulate_interval(self, interval_seconds):
        """
        Simulate a fixed time interval of customer behavior.

        Parameters:
        - interval_seconds: The duration of the simulation interval in seconds.
        """
        start_time = datetime.now()

        # Display the timestamp at the top of the status
        timestamp_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Timestamp: {timestamp_str}")

        # Generate random number of customers (up to 10) every 30 seconds
        amount_customers = random.randint(1, 10)
        print(f"Customers waiting to join Lanes: {amount_customers}")

        for i in range(amount_customers):
            customer = Customer()
            lane_type = assign_lane(customer, self.lanes, self.status_instance)
            add_customer_to_lane(customer, lane_type, self.lanes, self.status_instance)

        while (datetime.now() - start_time).total_seconds() < interval_seconds:
            time.sleep(1)  # Simulate time passing (1 second per iteration)

            # Simulate the passage of time and remove customers who have finished checking out
            for lane in self.lanes:
                for customer in lane.customers[:]:
                    lane.remove_customer(customer)

        # Display the current status at the end of the interval
        self.status_instance.display_status(*self.lanes)

    def end_simulation(self):
        """
        Ask the user if they want to end the simulation.

        Returns:
        - True if the user wants to end the simulation, False otherwise.
        """
        user_input = input("Do you want to end the simulation? (y/n): ").lower()
        return user_input == 'y'

    def run_simulation(self):
        """
        Run the main simulation loop until the user decides to end it.
        """
        while True:
            self.simulate_interval(30)  # Simulate every 30 seconds
            if self.end_simulation():
                break

        # Display the final status
        self.status_instance.display_status(*self.lanes)


# Create a list of Regular lanes and a Self Service lane
lanes = [Lane(lane_type=f"Regular {i + 1}", max_capacity=max_regular, status="Open" if i == 0 else "Closed") for i in
         range(5)]
lanes.append(Lane(lane_type="Self Service", max_capacity=max_self_service, status="Open"))

# Selecting the first Regular lane as the initial lane for simulation
initial_lane = lanes[0]

# Creating an instance of the Status class to manage and display the status of all lanes
status_instance = Status(lanes)

# Create an instance of the Simulation class with existing lanes and status_instance
simulation_instance = Simulation(lanes, status_instance)

# Run the simulation
simulation_instance.run_simulation()







