import scala.io.Source
import scala.util.parsing.json._
import java.io.File

object Test {

  def lines(filehandle: String) : Iterator[String] = {
    val fh = new File(filehandle)
    scala.io.Source.fromFile(fh).getLines()
  }

  def main(args: Array[String]) {

    val f = args(0)

    for (line <- lines(f)) {
      val json:Option[Any] = JSON.parseFull(line)
      val map:Map[String,String] = json.get.asInstanceOf[Map[String, String]]
    }

  }

}
