CREATE DATABASE PicMoney;
USE PicMoney;

CREATE TABLE perfil(
	id_perfil int not null primary key auto_increment,
	tipo enum("CEO", "CFO") not null
);

CREATE TABLE usuario(
	id_usuario int not null primary key auto_increment,
    id_perfil_fk int not null,
    nome varchar(300) not null,
    email varchar(300) not null unique,
    senha varchar(300) not null,
    foreign key (id_perfil_fk) references perfil(id_perfil)
);

CREATE TABLE menu(
	id_menu int not null primary key auto_increment,
    titulo varchar(300) not null,
    url varchar(300) not null unique
);

CREATE TABLE perfil_menu(
	id_perfil_fk int not null,
    id_menu_fk int not null,
    foreign key (id_perfil_fk) references perfil(id_perfil),
    foreign key (id_menu_fk) references menu(id_menu),
    primary key(id_perfil_fk, id_menu_fk)
);

CREATE TABLE regiao(
	id_regiao int not null primary key auto_increment,
    bairro varchar(300) not null,
    cidade varchar(200) not null
);

CREATE TABLE parceiro(
	id_parceiros int not null primary key auto_increment,
    nome_parceiro varchar(300) not null,
    categoria_parceiro varchar(300) not null,
    id_regiao_fk int not null,
    foreign key (id_regiao_fk) references regiao(id_regiao)
);

CREATE TABLE player(
	id_player int not null primary key auto_increment,
    nome varchar(300) not null,
    celular varchar(300) not null,
    idade int not null,
    genero varchar(200) not null,
    dataNascimento date not null,
    cidade varchar(300) not null,
    bairro varchar(300) not null,
    email varchar(300) not null unique
);

CREATE TABLE campanha(
	id_campanha int not null primary key auto_increment,
    nome varchar(300) not null unique,
    id_regiao_fk int not null,
    foreign key (id_regiao_fk) references regiao(id_regiao)
);

CREATE TABLE cupom(
	id_cupom int not null primary key auto_increment,
    codigo_cupom varchar(300) not null unique,
    valor_cupom decimal(10,2) not null,
    tipo_cupom enum("Desconto", "Cashback", "Produto"),
    id_campanha_fk int not null,
    foreign key (id_campanha_fk) references campanha(id_campanha)
);

CREATE TABLE transacao(
	id_transacao int not null primary key auto_increment,
    valor_transacao decimal(10,2) not null,
    valor_repasse decimal(10,2) not null,
    data_hora_transacao datetime not null,
    id_player_fk int not null,
    id_parceiros_fk int not null,
    id_cupom_fk int not null,
    foreign key (id_player_fk) references player(id_player),
    foreign key (id_parceiros_fk) references parceiro(id_parceiros),
    foreign key (id_cupom_fk) references cupom(id_cupom)
);