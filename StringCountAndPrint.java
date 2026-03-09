// Online Java Compiler
// Use this editor to write, compile and run your Java code online
/*
Write a java program
Input String s=“aaaabbbcceddaafffffabbb"

Output : a4b3c2e1d2a2f5a1
Input: "ramenr"
Output: r1a1m1e1n1r1

*/
import java.util.*;
import java.util.stream.*;
class Main {
    public static void main(String[] args) {
        System.out.println("Try programiz.pro");
       String s="aaaabbbcceddaafffffabbb";
   String sSplit[] = s.split("");

   HashSet<String> noteUniq = new HashSet<>();
   HashMap<String , Integer> chrMap  =new HashMap<>();
   int signCnt = 0; String charCntString ="", finalStr="";
   for(int k=0 ; k < sSplit.length ; k++ ){
         String singchar = sSplit[k];
         if(noteUniq.contains(singchar)){
             signCnt++;
         }
         else if (noteUniq.size() ==0 ) {

           noteUniq.add(singchar)    ;
         }
         else {
             chrMap.put(singchar , signCnt);
             signCnt = 0;
              noteUniq.add(singchar);
            charCntString =chrMap.entrySet().toString();
            chrMap =new HashMap();
         }
       finalStr += charCntString;
   }
        System.out.println(finalStr);
   /*
    Map<String, Long> mpCharCount =
      s.chars().mapToObj(ch -> Character.toString((char)ch)
            .collect(
                 Collectors.groupingBy(Function.identity() ,
            Collectors.counting()));

    String ar[] = new String[0];
    mpCharCount.entrySet().stream().forEach(entryEl -> {
       String nonReStr = entryEl.getKey();
       Long cntRe = entryEl.getValue();

       ar[0] += nonReStr+cntRe;

    });
       System.out.println(ar[0]);

      */
    }
}