(in-package :hello)

(defun main (args)
  (if (null args)
      (format t "hello ~A~%" *default-name*)
    (hello args))
  )

(defun hello (names)
  (when names
    (format t "hello ~A~%" (car names))
    (hello (cdr names))))
