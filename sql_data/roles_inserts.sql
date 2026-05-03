-- Insert data into roles
-- Generated at: 2026-04-21T14:16:56.353755

INSERT INTO roles (role_name) VALUES ('Chef') RETURNING id;
INSERT INTO roles (role_name) VALUES ('Waiter') RETURNING id;
INSERT INTO roles (role_name) VALUES ('Manager') RETURNING id;
INSERT INTO roles (role_name) VALUES ('Bartender') RETURNING id;
INSERT INTO roles (role_name) VALUES ('Cashier') RETURNING id;
INSERT INTO roles (role_name) VALUES ('Host') RETURNING id;
INSERT INTO roles (role_name) VALUES ('Busser') RETURNING id;
INSERT INTO roles (role_name) VALUES ('General Manager');
INSERT INTO roles (role_name) VALUES ('Location Manager');
INSERT INTO roles (role_name) VALUES ('Sous Chef');
INSERT INTO roles (role_name) VALUES ('Line Cook');
INSERT INTO roles (role_name) VALUES ('Delivery Driver');
INSERT INTO roles (role_name) VALUES ('Analyst');