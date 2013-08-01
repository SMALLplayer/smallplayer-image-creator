import base64
import random
import urllib2
from helpers.encodinghelper import EncodingHelper
from helpers.jsonhelper import JsonHelper


class Encrypter:
    def __init__(self, movieId):
        """ Creates an Encrypter/Decrypter for the 123video.nl site for a certain movie id

        Arguments:
        movieId : int - The ID of the movie

        """

        self.encryptionM = "@rdzl*ZnmbY$5xamWoOOxxA^QWs^Ku1UoOc^wdVOEf$na8BHhO-Bc%Qw5J8O%LKNZSD27p@7lBfPg2rw6*gZa~h!js44Q=gTkJdx2ru&cLVtIzJc6qj1aQicL%!PC!**a7*@2a%TMWZ@Hi#zz~bMx@eW!xMx4j9-VAuSWJzzX#JS2gUmuN0qjVieU=TSErpxXZ-8*h0^Z~HV^-rt*0ZdQdJ$c5K91xCdVaYK04v6WbRky=@F&m#qCYpbK6gDTi!SszN=Gq4ld08iyG0AqrRtW6l@9!W-&fjw-lsk2F%B5E%QcMBztDNXd=ca%1uSPLpU2TgP^gS5!Noqv30Cvdk~6gTTlRVpA4U#KFOpWJBv7ykaxSD9GN=b~l-xPe6cuX5l-LvI3Yj4CDMGPsRrP$KKJ*i1Qsy-xX7wJJr~efJdy05ckjvJz-0kc1ooDJF!Nyj1Cnb5lbwm4FM$H61Aef76F4aF@8q!*PBH7uGdx$gmYNsDPOP%FfcB5CdDi=eEEyE%QSexS1*2Y*b72NI#Cd36NNj^OjefsyrOxp!#PWDUF6=e0OcfJ2GNCUSiQi^-Dp^WFiAhau7Iljheuo$3c^~r!MN~5Ugn~3UeFB!wo4wgUlv#!Isx=VbttJho$9D!!1s$QOX86ipC@qz--*I^IlBhS2ZxG*ikTMb0riCSS%8dnXz%UhF00&HOLMK!=8MmWBNaJPjuL1F#8M~HI&S@0FZg%6C5ynJJqp8&U3gaw=xKMRhyho$3Jb=npx%zf9NBvpXuSlRpSaAtwDRjXBjrdWe$%Rp#7WUyXukd5eoAdgjWKLA*DYran%mt37Dmq530Vf02KPsbYfC3LtnMKKS6esJu2xmQhRPLzJmdC*9Xbl#~p9xm-qG1gS3U1!CLMAHPIBGud2W4-wxIs@^X4bR$pvn%IM!Fd2mpRcN*mHKE4=cA6&nfOZClYL#BoI^8Ed436^nrQfue=Kg1NM3QnwD-BXIzrcg^g%e$pBrLqgwPU-DIzZu&EB5nGA$cqA~G3IiyRLfoncuWkM!ftQnD1yN2j^vDhiK7U@=y!27K8xxa@uucwr!kVz78R9qD1#Pba9&@$2xBujRH#y*Ip-9kVGMo9P0Z^wvyB%Cr5RLlGk2^YGvu9*bVmqeIc-nwA07$*99ZMu~sc5#WJXq1~qE-3^socozP^fm&!b9hfeJyBbMy#OI3lGE6U=I4--~QPqidC*@3Q-7v&Ykk=UkLyA*J*cKWOBO0!ZFJ^g28EkyYVOcvg5EqUtpmq~0%eRP$zDb1vbK^YpV2Aydo3^w*5ZqqCmarQ7Qdz2Qf&k1Xf-3UPa0Tdeh#E$na&20tp%xcdTO-#XhO0!iML3=HgRzginNvyc@iluwhwU#CrUNGYo=EQ=zEfI#XGEeTN1ZW-fc#x%rw-Kad5Mau#idX#xde3hb1%XdF0WvmYlxSw*Zx2LiNA%N^Lh8XL6a$EoeY6~sfPkEU^#Lsf!52qbk39HQ5ptij5oi6g0F~f4SHMSsQ-%~qKQzqonNn2rMd%OT8V5~KHkf8wE9tyqc6IrWRs@7T#Gz~j1ZeJ*Xh~jWVVWtIS#Z%#$FHO@Pd15@r4seSc#VLJ6QoCs9mjJK*u4NhhntABFX3tVv-e!1H~oggN34&-mvN1PXhW8qF41&ISTab7PMvGtwwt8hL1vllwA8kF=IYbdMFx8aK0n!t=M^0o$Yej4E6vHz$P2S13ingjWEN6APWfQs4gKLMGM5d@lpEnoY8T7PL%sa$KPMOB9*!quK~yyMK9AG!6BjDe-$Hk1DbYOUJL%sn6fH3HG5ToX-lkBZ6*WH1fR$Jm8%Hz9aZpyOy6!X1X!%Nn%E9~m0DSf2k63$6l$f$r@U6Lop-LnAty@c~gaWm4bDcr^DPANC4GzUWjB1LUYVXVEYsT4rLasoM5Oe&T3VWJT9%$oKXt8!@HTBvNNpAAcrCg~oEM438Er7Lsbj9YBKsBdC~8F*k42m98Cd3toF@~0O6%7!olqjfl#AmD$IrgZbtZoJwnY!GQ$2a4=v-q8cYHd6U7GIAReJxJafPTy&YtlSVzVcI6Ny37O@h2dGx=*w%xntx28=jBbENM9GEufeJ5z^FXp31*L3Hs4lSukU9*gTwzHTVZ!HH%ipGhyPm&QAY%kPg!uQVoi@$P!GsnkcF4Wp&biPH6D6srSY=XgiT8y-ckBdKfv~CH3$dE!7&6@ifC#NDIZIGOh6^5Bq7IUb#bxG@^NA=OLN1hbywrm=-eBpU0z3oX^XONyOLAVMSEQJ^3RCRFxiSAyl$-~pk4#XYbDkiW2gBQLKYTT9w0W-*lNhGtSVw@jYZpx6^ndrciRmv8X$iYqP*TYQ0hYhMGjuTln2&J~ccQ0hplPljUVW4N#&gv6W4Oxfl9LFAa2Dh#!Up0#pmC%*nn5o5K*hje$m-1^8sk!Zm6O7WmZK=t#17UiU7hwjR@9U4KLJJ^-9AnSp=IuAESyXWJS1W$~Ec4N2cV$tLVk8AGpbYNabY!DI4LVmscPL0#j1X*!N585DCq@p!t^oV~5&Ezfz!^5xuHI&SPYbRw3MjJbiD^du08a-h*Vdyb%M#TaYEV^Hd6Vru~8X25M8YSuz7hhr7StCn14as1*f&z2Uo=KeDn9%gKm7w8lVsBdK*SjwvRt*sCqC&wi63$vSqlQ5A8NeaGC#3V$volY&D~wZFxn!YEN79YraR2z6!~8wYTugTt1LGHde01y9nFht3QVc7@MRTa26QkYAc~SssUEzUULZHLOwn9KVXDFT0n00YQ*XwdXe3A20^Zp9%v3WB=X-t@DbIpzq7yGh1RFQ&rbDj6%TKAy2pkGF$b7Ikus2KFQroS^!5!bPxYQgR~ltsKVZOeKK@$YhL5gJ7RNHrm#M~jI7#IQUf#Sy&0HOEnQL@0Plih2f%aX^=DCekIE!Wxk~z7V9gq45IKUbpCvq&3ayyF@CZXmAMFI7iXV5He3^T#Jc8XkvR^3lys-V^%5RK0og03pH2lK3#i=-&gJH-gr8Pe&s%ufI59sO6GknEW4DkOoSlWKAwCYRaT5neU#qqD1&^FDK$qF7lajDpz#gNiHj#Ab$~-R0-&KHU2IHtJVzxQ&8Wwj=qk6FMNG9bXfLCNf-@-~D#g%qY20Pr$Zj4b8!U%6i*=ac!jFW%USfV!y2WI7Yvp1*BT$ABcZQwK!&T&o0!9v0q6tqtR83AhRhSvdG1F@jtzU~itzGXa9A*M@%Q=IuJcg09!wwkl5FlhD3YKF6=WPRxIq9f@%bnW=tvuPO~dIYd4&2bKu71nJlxto1&9dxm7~jJE*U9CV4*au9rsYrZtGHpNCo!~~TLY-yi%-~4y=JEEuiX6lCGTkESyfi#IG5uPDWDT1%CaWzXkPY8nM&LOCat7^7A1KP0wlqRPr8REv9YiroRBk8cHs3Eoup#eZjuu#vRQ5cNZqrbeUl2y0F-1yvum~hKO*~ViGDJ6UQCjlZy*Eqw7&=j8VoFdjRuR7jd%@xiXwLg4pHBvFpBQS~OqUcw!wYuc8oRyUz!z~6fy*Oy^@vR&SQT3s1zOF~ejttI@D*GmJ%SFV=p~z9@KpQDtVW9tYVCCfgmd=t@#9XO&ztx$-B0kj0!MS109uuCMFelB$u4we7-tEfv5r@Dd&#UBfjWoLBXRWfdBfw=!R0wzyu7l0~Yy&E9J!1k^TZJ6@wasK0tODo=fFSBJazU$gNnm!ZTfMaf^Uo&NkP@dbS^~RM0k2xnJmzoT85Pa^x4NozE&Eo30Yb0Hrx$Xt=$QL7ANOdDRUYiJe4pyUBjaXXrdlW0o~$smmlr#vaVivW*b@ck9Gtm8kt#7I^-g@TT*jptT9$55wST@o84Bzte=@V1d@jc6PcWlnqcgbm$ztJv$WtGd1Bx1&wpVvhad57xBc-TpaU7Scfk1goi^Q*%oUmrF6eqmpH8Rq6oET5F8TpBq1JY4-%-BnxL5g5T&HcW2vrnwpAI6!4ml8giFf^Zk7C0V~hELQRE~JxuOjCs&BR!Wmv&h~agJcDmVT85nRMR*7p$rzY01#gt6X&vRY8Il6=%jog8n23!h3#KES~Fq&fxcHRoknY0GSs%7nqJAlWsWePRd4Pd!NOxm-3^!-rh4yViXA7b4sH^hXgG3q2IXp=c"
        self.movieId = movieId

        self.salt = self.__GetSalt()
        self.publicKey = self.__GetPublicKey(self.movieId, self.salt)

    def DecryptWithKey(self, data, publicKey=None):
        """ Decrypts in input message using a publicKey or the publicKey of the instance

        Arguments:
        data : string - The data to encrypt

        Keyword Arguments:
        publicKey : String - The public key to use. If none is specified, use the
                             class key.

        :: Take from the 123video.swf ::
        public static function decryptWithKey(param1:String, param2:String) : String {
             var _loc3_:MacEncryption = new MacEncryption();
             return _loc3_.decrypt(param1,param2+_m[1865]+_m[4007]+_m[2625]+_m[34]+_m[3896]+_m[349]+_m[776]+_m[471]+_m[2855]+_m[31]+_m[3419]+_m[855]+_m[3660]+_m[3016]+_m[1736]+_m[1862]+_m[2365]+_m[2590]+_m[1756]+_m[317]+_m[2330]+_m[3407]+_m[1512]+_m[966]+_m[2514]+_m[3211]+_m[3935]+_m[21]+_m[2297]+_m[852]+_m[156]+_m[850]+_m[2577]+_m[597]+_m[3332]+_m[326]+_m[3711]+_m[91]+_m[2472]+_m[1673]+_m[7]+_m[2583]+_m[24]+_m[3223],true);
          }
        """

        if not publicKey:
            publicKey = self.publicKey

        m = self.encryptionM
        decryptionKey = publicKey + m[1865] + m[4007] + m[2625] + m[34] + m[3896] + m[349] + m[776] + m[471] + m[2855] + m[31] + m[3419] + m[855] + m[3660] + m[3016] + m[1736] + m[1862] + m[2365] + m[2590] + m[1756] + m[317] + m[2330] + m[3407] + m[1512] + m[966] + m[2514] + m[3211] + m[3935] + m[21] + m[2297] + m[852] + m[156] + m[850] + m[2577] + m[597] + m[3332] + m[326] + m[3711] + m[91] + m[2472] + m[1673] + m[7] + m[2583] + m[24] + m[3223]
        return self.__Decrypt(data, decryptionKey, True)

    def EncryptWithKey(self, json, publicKey=None):
        """ Encrypts in input json message using a publicKey or the publicKey of the instance

        Arguments:
        data : string - The data to encrypt

        Keyword Arguments:
        publicKey : String - The public key to use. If none is specified, use the
                             class key.

        :: Take from the 123video.swf ::
        TopLevel::       public static function encryptWithKey(param1:String, param2:String) : String {
             var _loc3_:MacEncryption = new MacEncryption();
             return _loc3_.encrypt(param1,param2+_m[3752]+_m[2486]+_m[3751]+_m[3826]+_m[2563]+_m[2012]+_m[3850]+_m[1423]+_m[1537]+_m[1882]+_m[162]+_m[2348]+_m[3130]+_m[886]+_m[3298]+_m[1168]+_m[1456]+_m[2893]+_m[1183]+_m[2694]+_m[855]+_m[753]+_m[3924]+_m[982]+_m[17]+_m[435]+_m[3701]+_m[3567]+_m[1038]+_m[4017]+_m[229]+_m[730]+_m[1514]+_m[1685]+_m[1714]+_m[2452]+_m[1964]+_m[1897]+_m[2111]+_m[1515]+_m[680]+_m[1054]+_m[3877]+_m[3816],_loc3_.getSalt());
          }

        """

        if not publicKey:
            publicKey = self.publicKey

        m = self.encryptionM
        publicKeyToken = publicKey + m[3752] + m[2486] + m[3751] + m[3826] + m[2563] + m[2012] + m[3850] + m[1423] + m[1537] + m[1882] + m[162] + m[2348] + m[3130] + m[886] + m[3298] + m[1168] + m[1456] + m[2893] + m[1183] + m[2694] + m[855] + m[753] + m[3924] + m[982] + m[17] + m[435] + m[3701] + m[3567] + m[1038] + m[4017] + m[229] + m[730] + m[1514] + m[1685] + m[1714] + m[2452] + m[1964] + m[1897] + m[2111] + m[1515] + m[680] + m[1054] + m[3877] + m[3816]
        return self.__Encrypt(json, publicKeyToken, self.__GetSalt())

    def __GetSalt(self):
        """ Take from the 123video.swf

        public function getSalt() : String {
             var _loc1_:* = new ByteArray();
             var _loc2_:Number = 0;
             while(_loc2_<16)
             {
                _loc1_.writeByte(randomNumber(1,255));  --> Writes 8 bit bytes (255 max)
                _loc2_++;
             }
             _loc1_.position=0;
             var _loc3_:String = Base64.encodeByteArray(_loc1_);
             return _loc3_;
          }

        """

        i = 0
        bytes = []
        while (i < 16):
            bytes.append(random.randrange(1, 255, 1))
            i += 1

        # bytes to chars
        data = "".join(map(chr, bytes))
        data = base64.b64encode(data)
        return data

    def __GetPublicKey(self, movieId, salt):
        """ Take from the 123video.swf

        TopLevel.Variables.PublicKey=MD5.hash(TopLevel.Variables.MovieID+this._m[2848]+this._m[2961]+this._m[3415]+this._m[2698]+this._m[1700]+this._m[2052]+this._m[2055]+this._m[2022]+this._m[2563]+this._m[3416]+this._m[1995]+this._m[1141]+this._m[469]+this._m[1590]+this._m[1751]+this._m[1554]+this._m[1687]+this._m[2616]+this._m[3148]+this._m[4013]+this._m[633]+this._m[3774]+this._m[559]+this._m[823]+this._m[228]+this._m[773]+this._m[2718]+this._m[3246]+this._m[1958]+this._m[680]+this._m[2318]+this._m[1721]+this._m[4078]+this._m[2955]+this._m[4022]+this._m[2609]+this._m[3786]+this._m[3306]+this._m[1163]+this._m[2005]+this._m[3715]+this._m[2142]+this._m[3509]+this._m[3894]+this._m[1334]+this._m[3269]+this._m[3615]+this._m[3775]+this._m[3269]+this._m[3781]+TopLevel.Variables.Salt);

        """

        m = "9%j7FR7EEY@mmtMsooBJo%MhDW#GQSPbLGzsSDNiycweHbni#%gQ14Nbd=V56-bdhvr3B68==fi8PMv04mR6AUs=Z7WNYuIjp337lAhNG7KIb$PJU=4&YMS1!1&URrwQNWuXl6w1druxsxLyoZ*gTJ9cmSL1M0SPq-R0&QEHb$9nzA4e7FXLxSphp*cZ^g5XNudz1itj-#BlR0fJa!JNrv2#Vw%A1CtTzMtCsj49yUzRBW@JhX=Xj&CZcy^MeZ-6EbUOlCU-QL~IIb#t=4f9-t%&Xb#Gj4M%bOv3sVNvvzVk~IVX5pAr24GBteHZq8tQoKGoBQOAMs2xiFI9Xe6=mr8UklFbrx0BoxZ*rRYPTetxBHaYR*H0!T*!D52VXU3nhl=U8vyoixueQqz~%9uMg!VW3wiW0dgJ2=^j#81MgNZ0Fpp*BvmLSli-1!E&eKKHJS2H6NJ9&^MLLWJCa^l%e5A8I4@3rW!IO=76a8uFKximyYIQUyw3AeYQjmqnLyiDfBiLcXNT6C0IVDwUGalgEFH9OQKY9NKh7~dyl#UFT9E*XK3dqw#7Nl~#JQSg7XV6#7Zi9t37=BwOAHUfx%tdbPYQQ1G=QY1kwK3i5FrDf~YY=@Z1G@Lnx&fR&Tr0j2X-3REGEEHnCP@WWMWC6P8CTVCbl*dAGuUSX*Cn$~Gr%LOtnjIHrY5npVG74KRY4UmGc7PEgDl3#JD#-4!r1y7NXlmLyLPt=xx$P3pAgIKTgxHXUlDk*eDEfR2A26QTA%7YhRQ3iOsR^kxfBYt8w-g365d3Q^3HtzDGQs$9-~euNkL@0!ed4ai%Ykodz8tcWo!feED4wyhDPA1&*q5V&SYbjSNQ0211kH!#-F&DAEH6Bz~SE#^Xl13SGcsGid%0twp1ux0mbkcbX8ugigyJ4Eo@iFvj$XJG*D9MzIiYB-5RK-7jqDfHB3Vz-lRJbs67Q6YOfTOnK37WddcC~Ti#tnjyX&OSD0hn8#8nvjsaJ2pSD@Ge9STzOS8ppX2RcKyX#^F7R&S0$IhonCsNvd0RW!kVOVKCTtc=ZAZucB0FmF~5felLaflyE4PJu0C=kCw6Pu*n~@1ABExVsn48KLuUhwfaj#8xwwEo-Z-f-fm-F5uPWlpj1kN3ovni@BELb$qkyr4jQ3V%oW@xwZ^n8$U7d-jXNnfO=YSYG*HdvVFnxYz=f%2C8m$&vB75H7BKhiMaa=19#ybeNiXJj&uzMqSmzt%GENX3g$vnV809~3uPC-ILRXhm~e#GTP&HAewh7Z!2nUynQKpMla5R&JCvWvnAuLvtVesJ29paLD96@@iyPDVjwSchUyS#A9SR^MR!KNduYse~S#-C*eUxq4WNi@Sa9hPN3%y1MLoM2veQvCsnPSy~PO4S*ei#T*LFP%HFI0c%iPuRR*jd0IpZ4tMFC&mn9F&zvb8Vm#iHm4IkHCzd5$f~T~pp3A^Mm7rrRQhsNCZo$QfpaIkdSzjPR!^2dmAHuoC=S00MObXR@uK68e!*OEdq@6S98!9lD85ZLFrDMI!ZFCYAEoG6BKL1ACX9&W^dIeRu=@l=o&JB9%&sQ=NxecESuyIUb*bosbaGN9P2qfntjQ#2bKRwP73UvB1qcDIwwGbS7b-OzoTv1JDGF32MSokyps%J0n~8hXV6xtezJ^*7gpV09AOWyMB*oEAtu%GuaffyUVom3~oc-23AbJHR8#Px*~J9UwSvs3^fD3dn%d-QH4$^T4!V$$ggPoat%4kj^rtJkJHa#nS~DGG*v=vqp!Fi%mnnst9-TXIjaQaGX9nK#xa6&tUxchwd8cDXhdeJ@=yFcZ2uv%hhsCgSFbB^5tDi6zZKp3qJob9zua^T2~Rwro$r4L9YE=R5SKUAZ2%RaMuCQj!YQxB=IaA27BKjkFag2a~48OOw@gT5IbQ$tgQnXVlrF78arvc4QxC@RUTxAoRQq2Hbq$F-mFKA^LL$RECktME88F8GKFH!wKzox%iF#mK$-y2pkZtqoLAZ2*0b2dK1ZuCIeAOT#DGS&GNaj5DYux8T7T^1RkC!LY!g$N@ZZ~lWc~j=VE#AHfUF@gAAw*rmdP$BqdK&#ih6i!2bcNr4N%6W41gKAF5vg84-z-ff^mBGPi&HKgAYhsgv!JU^nuIB=$Y!$p6A~zx2zOkY*&85^9^WNLVG#13lRHAgs=yGQkvM7YeydN&*jRowj-oMW4X75F5R5tAc*P0g5hQC^EWOrnlNVLq$HeJ7-znmcIq^1m7fA20oXnM%RK3Ioy%!G6zox%Eqf=46^qR#K3cC0Nc$lH=mrCJY-Ewv6NRVzkooR-*sp3aakj#Et%&--OyvF$pcL=YO-c9Fj68OkOEbA@4~S=9MfekyqxH%GEd^s^d4zHjqA=J-F1JzRn^c%94~s&HNZT@Waxt#a!DDbrV6y&=qYPyguKLBt*5bH8z&hdxYsh-Tp4FU7Gk5K4aMi&F@dprn@M$zHvzg*fAwgIrG6JHccIqgS7#A@9H5Qe=QlBmZ4h-tKhj4=3QYjTjR@bMqKY58QmwuV-H~nZ@hZKbh5UAA0O1~7Ez0nv-c&!iB8gMhmeg~T8jiXc$@pcw~j8Lr$g!SYr3ksL8XSUK7Jhz5wX~D#SyIekVfYzgD1sffYrOaYa&e#NOUvskGqg3A2f-$~mWM3tWFn~myvG7cea*PDBS1~SP$ZBRVRdqJ^Tq=FP3sXWhi5xQ&Kdr#NgPympJssd*aD@rfA~q4T4$h-Bq$Ci02@lSOECmTlNz0V5am^zUEo-mTkquqNFe9bWasQ3Y0LkxbwU6@ou~N*p1cH*Uv3G08Q@zRf6%gPLw~6c3fp^dtEm#0E7-Fu0&%$~!nMMLfjVf!@ybcnGfeamlMuIKKx72MksB-00vAyAUXz9$1fv1ibTds%wWluik*iPd9^xco10=D9Uzg9&ZX#W8HBJCWO7qP3jKwod939PcfDqC5vrVqn7%qZgfpe1!qvqbG4xUGd@R6RYztL^$p6!oeu~jJX3kEzYLz0V28TL3$t*l4tMk6e8T~DmBlWasy*h2FsT5XTx1QGi38^8F&IK8O4j=mLwRCq&5hTnnvsI!njYEEd9vd=13v9X41CmHf#kIoU@iY8uODp*0d$3BreUwT=*rkDhI*-yjz5Il=BAC$#F=2~Zl!DErh7#U7DB%iRbzPg~tuJP2DJdTO&zn6DbaG-V$P4bUtiK2yp79nrJtpcb^!Uj0MCfIRLSbH~XB^nm1a!!CXF=M~kwCHuBHrmde&0#E7-VF=x6wZaqLu9I%U0E2gAPud$mIfWR1eU2$Vq*w6*Zpi5r0RL^zr3MJEeDp=pba0WnLdp2sA%Os6~CL$JKr@&LxYwkR~o4W^CPROsr9HWDi3kaAjRRaqlDBIdmx6~pQ#!Pbrv4YN6mP0uaW$WR76XJ@~1pw88hu=ht=IY1-ar3m6ngW%0!JSIXV42XW0BdbHVGAF^scgd~OJQRPjiOhNt&F2lvi@L$rYY~#OQkVWe8xlDSpl5H2PbYb29Ld8qvHwp*!ghz1LhEWWVJooXSThEcJJHt6s4MA~9c3ciyMznhzr6FsxN~$Ve1hxGxETuKcsGAPvm@UM^!WV@639vdBBlSsw6I4c&uK2pow6PtuzhFQpKS@PoS&pr7**w5b*qd&!&Z4IKG&*Xqs0MMRPg~Ap24Si55W$j8lJfnmBa&keN6rul=TpulEs&lkLOZ6ywTtpdeX%VDmTxmkM@xO~4g!LlIcM&jXsLNpmQ=lpchOkdXiga3l5V67mPhO%x#S4I@BW#*%vg=0-yNi*lJRjiC7IKL@GQIS0^IYCnL5iqejvVkMc*71P7~UNbW2~zbufa7ArR-UiYBCS87MQ50$WD4e*F&fFwK%QuGsuo7jCx*lI%t1#XLbUh#n0kJPFsGOTT3kS-*4T5o@xbCgzdD@DR^O9@cTP!h@Eory7w&U3PI1!jxeNjUIK=yf$&94l#u!c@4nri0ldAc0mo#ej^WRz*^~BV$O@DBO%dr*H8D!5B#CYkni@OqTVZUU6OLAK$NHKb6=ElY%tortc91Rvp!0H0A%hSZS6e8b0WX~#hJc3OmcVNMg7!O^^McZJXW@OP3epGnX@QTcB^JFtc#51%xLxyJr%%zP&TojX"
        data = str(movieId) + m[2848] + m[2961] + m[3415] + m[2698] + m[1700] + m[2052] + m[2055] + m[2022] + m[2563] + m[3416] + m[1995] + m[1141] + m[469] + m[1590] + m[1751] + m[1554] + m[1687] + m[2616] + m[3148] + m[4013] + m[633] + m[3774] + m[559] + m[823] + m[228] + m[773] + m[2718] + m[3246] + m[1958] + m[680] + m[2318] + m[1721] + m[4078] + m[2955] + m[4022] + m[2609] + m[3786] + m[3306] + m[1163] + m[2005] + m[3715] + m[2142] + m[3509] + m[3894] + m[1334] + m[3269] + m[3615] + m[3775] + m[3269] + m[3781] + salt
        return EncodingHelper.EncodeMD5(data, False)

    def __Decrypt(self, data, key, boolean):
        """ Take from the 123video.swf

         public function decrypt(param1:String, param2:String, param3:Boolean=false) : String {
             var _loc5_:* = undefined;
             var _loc6_:String = null;
             var _loc7_:String = null;
             var _loc8_:ByteArray = null;
             if(param3)
             {
                _loc5_=new ByteArray();
                _loc5_=Base64.decodeToByteArray(param1);
                _loc5_.position=0;
                param1=_loc5_.readUTFBytes(_loc5_.length);
                _loc6_=param1.substring(0,param1.length-24);
                _loc7_=param1.substring(param1.length-24,param1.length);
                _loc8_=this.process(Base64.decodeToByteArray(_loc6_),MD5.hash(_loc7_+param2));
                return _loc8_.readUTFBytes(_loc8_.length);
             }
             else
             {
                var _loc4_:ByteArray=this.process(Base64.decodeToByteArray(param1),param2);
                return _loc4_.readUTFBytes(_loc4_.length);
             }
          }

        """

        if boolean:
            loc5 = base64.b64decode(data)
            param1 = loc5
            loc6 = param1[0:len(param1) - 24]
            loc7 = param1[len(param1) - 24:]
            return self.__Process(base64.b64decode(loc6), EncodingHelper.EncodeMD5(loc7 + key, toUpper=False))
        else:
            pass

    def __Encrypt(self, data, publicKeyToken, salt=None):
        """ Take from the 123video.swf

        public function encrypt(param1:String, param2:String, param3:String=null) : String {
             var _loc4_:ByteArray = new ByteArray();
             _loc4_.writeUTFBytes(param1);
             if(param3!=null)
             {
                return Base64.encode(
                    Base64.encodeByteArray(
                        this.process(
                            _loc4_,
                            MD5.hash(
                                param3+param2
                            )
                        )
                    )+param3
                );
             }
             else
             {
                return Base64.encodeByteArray(this.process(_loc4_,param2));
             }
          }

        """

        if salt:
            md5Data = EncodingHelper.EncodeMD5(salt + publicKeyToken, False)
            processData = self.__Process(data, md5Data)
            processData = base64.b64encode(processData)
            return base64.b64encode(processData + salt)
        else:
            pass

    def __Process(self, encodedString, md5hash):
        """ Take from the 123video.swf

        private function process(param1:ByteArray, param2:String) : ByteArray {
             var _loc3_:* = new ByteArray();
             var _loc4_:Number = 0;
             var _loc5_:Number = 0;
             while(_loc5_<param1.length)
             {
                _loc3_.writeByte(param1[_loc5_]^param2.charCodeAt(_loc4_));
                _loc4_++;
                if(_loc4_>=param2.length)
                {
                   _loc4_=0;
                }
                _loc5_++;
             }
             _loc3_.position=0;
             return _loc3_;
          }

        """

        loc3 = []
        loc4 = 0
        loc5 = 0
        while loc5 < len(encodedString):
            loc3.append(ord(encodedString[loc5]) ^ ord(md5hash[loc4]))
            loc4 += 1
            if loc4 >= len(md5hash):
                loc4 = 0
            loc5 += 1
        return "".join(map(chr, loc3))

if __name__ == "__main__":

    def OpenUrl(url, postData=None, headers=dict(), proxies=None, username=None, password=None):
        """ Just a temporary OpenUrl method that can do a lot """

        uriOpener = urllib2.build_opener()

        if username and password:
            encoded_string = base64.encodestring('%s:%s' % (username, password))[:-1]
            headers["Authorization"] = "Basic %s" % encoded_string

        if proxies:
            proxyHandler = urllib2.ProxyHandler(proxies)
            uriOpener.add_handler(proxyHandler)

        fd = None
        data = ""
        try:
            if postData:
                req = urllib2.Request(url, data=postData, headers=headers)
            else:
                req = urllib2.Request(url, headers=headers)
            fd = uriOpener.open(req)
            data = fd.read()
            fd.close()
        except:
            if fd:
                fd.close
            raise
        return data

    def GetJson(movieId, publicKey, salt):
        """ Take from the 123video.swf

        Random:String(Math.floor(Math.random()*1.0E10)),
        MovieID:TopLevel.Variables.MovieID,
        MemberID:Number(TopLevel.getParameter("MemberID",0)),
        Password:String(TopLevel.getParameter("Password","")),
        PublicKey:TopLevel.Variables.PublicKey,
        IsEmbedded:TopLevel.Variables.isEmbedded,
        EmbedUrl:TopLevel.Domain.embedUrl,
        AdWanted:(TopLevel.Variables.isEmbedded)||(Boolean(Number(TopLevel.getParameter("RequestAd","1")))),
        ExternalInterfaceAvailable:ExternalInterface.available,
        Salt:TopLevel.Variables.Salt

        """

        json = dict()
        json['Random'] = "31415926"
        json['MovieID'] = movieId
        json['MemberID'] = 0
        json['Password'] = ""
        json['PublicKey'] = publicKey
        json['IsEmbedded'] = False
        json['EmbedUrl'] = ""
        json['AdWanted'] = False
        json['ExternalInterfaceAvailable'] = False
        json['Salt'] = salt
        return str(json).replace("False", "false").replace("True", "true").replace("'", '"')

    movieId = 1202280

    enc = Encrypter(movieId)
    # salt = enc.__GetSalt()
    print "Salt: %s" % (enc.salt,)
    print "PublicKey: %s" % (enc.publicKey,)
    json = GetJson(movieId, enc.publicKey, enc.salt)
    print "Json: %s" % ([json],)
    result = enc.EncryptWithKey(json)

    url = "http://www.123video.nl/initialize_player_v4.aspx"
    data = OpenUrl(url, result, {"123videoplayer": enc.publicKey}, {'http': 'http://localhost:8888'})
    result = enc.DecryptWithKey(data)

    jsonData = JsonHelper(result)
    hashes = jsonData.GetValue('Hashes')
    locations = jsonData.GetValue('Locations')
    videoData = (locations[0], enc.publicKey, EncodingHelper.EncodeMD5(hashes[0], False), int(movieId / 1000), movieId, enc.EncryptWithKey('{"Salt": "%s"}' % (enc.salt,), enc.publicKey))
    videoUrl = "http://%s/%s/%s/%s/%s.flv?%s" % videoData
    # "http://"+param1+"/"+TopLevel.Variables.PublicKey+"/"+MD5.hash(TopLevel.Variables.videoInfo.Hashes[0])+"/"+TopLevel.Variables.MovieFolder+"/"+TopLevel.Variables.MovieID+".flv?"+TopLevel.encryptWithKey(com.adobe.serialization.json.JSON.encode({Salt:TopLevel.Variables.Salt}),TopLevel.Variables.PublicKey);
    print "=======================\n%s\n%s" % (jsonData.json, videoUrl)
