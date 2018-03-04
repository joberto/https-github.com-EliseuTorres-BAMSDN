 BAMSDN 
========


Trata-se um modulo que permite a um controlador SDN, gerenciar de forma dinâcia a largura de banda das portas de saida dos switches OpenFlow através de filas de classes de tráfego. 

Os  experimentos seguiram uma abordagem de emulação que reproduziram uma rede OpenFlow atraves do Mininet. Para isso, foram utilizados.

      1. PC Corei5, 2.9Ghz, 8GBdeRAM
      2. Sistema Operacional Ubuntu Server 15.04,x64, versão do kerne l3.19.0-30
      3. Mininet, versão 1.8r11
      4. Protocolo OpenFlow, versao 1.0
      5. Controlador OpenFlow POX, versao 0.2.0
      6. Gerador de trafego iPerf3, versao 3.0.7


Qualquer ambiente Linux com Mininet, OpenVswitch, OpenFlow e controlador POX deve rodar esse experimento sem problemas.

Cada controlador foi projetado para a seguinte topologia.

https://github.com/EliseuTorres/BAMSDN/blob/master/Topologia.png

============================================================================

Para a utilização do ambiente siga os seguintes passos abaixo.

Baixar o código fonte do projeto.

     git clone https://github.com/EliseuTorres/BAMSDN.git

Mover os scritps mam.sh e rdm.sh para o diretorio /pox

Mover as pastas MAM e RDM para o diretório pox/ext

Por meio de um terminal execute os scripts mam.sh ou rdm.sh para executar um dos controladores

      $sudo ./mam.sh

      ou

      $sudo ./rdm.sh

Em outro terminal execute a topologia lab.py

      $sudo python lab.py

No CLI do Mininet digite

     <mininet> xterm h1 h2 h3 h6

O host h6 será o serividor, acesse a pasta scripts e execute todos os scripts

Em h1, h2 ou h6 faça a conexão ao servidor.

      iperf3 -c 10.0.0.6 -p porta_de_destino

Para esse experimento dividimos as classes de trafego com as seguintes portas

    CT0 5001 a 5100
    CT1 5101 a 5150
    CT2 5151 a 5200

Acesse o video para visualizar um simples teste.

https://youtu.be/BNcH2l3vwPQ
