-- Insert data into roles
-- Generated at: 2026-04-19T14:26:33.586472

INSERT INTO roles (role_name) VALUES ('Chef') RETURNING id;
INSERT INTO roles (role_name) VALUES ('Waiter') RETURNING id;
INSERT INTO roles (role_name) VALUES ('Manager') RETURNING id;
INSERT INTO roles (role_name) VALUES ('Bartender') RETURNING id;
INSERT INTO roles (role_name) VALUES ('Cashier') RETURNING id;
INSERT INTO roles (role_name) VALUES ('Host') RETURNING id;
INSERT INTO roles (role_name) VALUES ('Busser') RETURNING id;
